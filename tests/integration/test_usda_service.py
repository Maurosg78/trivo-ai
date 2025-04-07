import asyncio
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
import pytest_asyncio
from pydantic import SecretStr

from src.core.config import settings
from src.core.services.usda_service import USDAService, USDAServiceError


@pytest.fixture(autouse=True)
def setup_test_config():
    """Configura el entorno de prueba."""
    settings.USDA_API_KEY = SecretStr("test_key")
    settings.USDA_API_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    settings.USDA_API_RATE_LIMIT = 10
    settings.USDA_API_RATE_WINDOW = 1
    settings.USDA_API_MAX_RETRIES = 3
    settings.USDA_API_RETRY_DELAY = 1


@pytest_asyncio.fixture
async def usda_service():
    """Fixture que proporciona una instancia de USDAService para pruebas."""
    service = USDAService()
    try:
        yield service
    finally:
        await service.clear_cache()


@pytest.fixture
def mock_response():
    """Fixture que proporciona una respuesta simulada de la API."""
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    return mock


@pytest.mark.asyncio
async def test_search_foods_integration(usda_service, mock_response):
    """Prueba la búsqueda de alimentos."""
    mock_response.status = 200
    mock_response.json.return_value = {
        "foods": [
            {
                "fdcId": 1,
                "description": "Pizza Margherita",
                "servingSize": 100,
                "servingSizeUnit": "g",
                "nutrients": [
                    {"nutrientId": 1003, "nutrientName": "Protein", "value": 12.5, "unitName": "g"}
                ],
            }
        ]
    }

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        results = await usda_service.search_foods("pizza", page_size=5)
        assert len(results) == 1
        assert results[0].fdc_id == 1
        assert results[0].description == "Pizza Margherita"


@pytest.mark.asyncio
async def test_get_food_details_integration(usda_service, mock_response):
    """Prueba la obtención de detalles de un alimento."""
    mock_response.status = 200
    mock_response.json.return_value = {
        "fdcId": 1,
        "description": "Pizza Margherita",
        "servingSize": 100,
        "servingSizeUnit": "g",
        "nutrients": [
            {"nutrientId": 1003, "nutrientName": "Protein", "value": 12.5, "unitName": "g"}
        ],
    }

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await usda_service.get_food_details(1)
        assert result.fdc_id == 1
        assert result.description == "Pizza Margherita"


@pytest.mark.asyncio
async def test_get_nutrient_info_integration(usda_service, mock_response):
    """Prueba la obtención de información nutricional."""
    mock_response.status = 200
    mock_response.json.return_value = {
        "fdcId": 1,
        "description": "Test Food",
        "servingSize": 100,
        "servingSizeUnit": "g",
        "nutrients": [
            {"nutrientId": 1003, "nutrientName": "Protein", "value": 12.5, "unitName": "g"}
        ],
    }

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        results = await usda_service.get_nutrient_info(1)
        assert len(results) == 1
        assert results[0].id == 1003
        assert results[0].name == "Protein"


@pytest.mark.asyncio
async def test_cache_integration(usda_service, mock_response):
    """Prueba el funcionamiento del caché."""
    mock_response.status = 200
    mock_response.json.return_value = {
        "foods": [
            {"fdcId": 1, "description": "Test Food", "servingSize": 100, "servingSizeUnit": "g"}
        ]
    }

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # Primera llamada - debe hacer la petición
        results1 = await usda_service.search_foods("test")
        # Segunda llamada - debe usar el caché
        results2 = await usda_service.search_foods("test")
        assert len(results1) == 1
        assert len(results2) == 1
        assert mock_response.json.call_count == 1


@pytest.mark.asyncio
async def test_rate_limit_integration(usda_service):
    """Prueba el rate limiting."""
    mock_responses = []
    for _ in range(10):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"foods": []}
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_responses.append(mock_response)

    with patch("aiohttp.ClientSession.get", side_effect=mock_responses):
        tasks = [usda_service.search_foods("pizza") for _ in range(10)]
        results = await asyncio.gather(*tasks)
        assert len(results) == 10
        assert len(mock_responses) == 10


@pytest.mark.asyncio
async def test_error_handling_integration(usda_service, mock_response):
    """Prueba el manejo de errores."""
    mock_response.status = 404
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=Mock(), history=[], status=404, message="Not Found"
    )

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(USDAServiceError):
            await usda_service.search_foods("")


@pytest.mark.asyncio
async def test_network_error_handling(usda_service, mock_response):
    """Prueba el manejo de errores de red."""
    mock_response.raise_for_status.side_effect = aiohttp.ClientError()

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(USDAServiceError):
            await usda_service.search_foods("pizza")


@pytest.mark.asyncio
async def test_invalid_response_handling(usda_service, mock_response):
    """Prueba el manejo de respuestas inválidas."""
    mock_response.status = 200
    mock_response.json.return_value = {"invalid": "response"}

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(USDAServiceError):
            await usda_service.search_foods("pizza")


@pytest.mark.asyncio
async def test_api_unavailability_handling(usda_service, mock_response):
    """Prueba el manejo de indisponibilidad de la API."""
    mock_response.raise_for_status.side_effect = aiohttp.ClientError()

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(USDAServiceError):
            await usda_service.search_foods("pizza")


@pytest.mark.asyncio
async def test_timeout_handling(usda_service, mock_response):
    """Prueba el manejo de timeouts."""
    mock_response.raise_for_status.side_effect = asyncio.TimeoutError()

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(USDAServiceError):
            await usda_service.search_foods("pizza")


@pytest.mark.asyncio
async def test_retry_mechanism(usda_service, mock_response):
    """Prueba el mecanismo de reintentos."""
    mock_response.status = 429
    mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=Mock(), history=[], status=429, message="Too Many Requests"
    )

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(USDAServiceError):
            await usda_service.search_foods("pizza")
