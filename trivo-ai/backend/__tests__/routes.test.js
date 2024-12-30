const request = require("supertest");
const { app, server, closeDatabase } = require("../server");

describe("Rutas del backend", () => {
  afterAll(async () => {
    if (server && server.close) {
      server.close(); // Cierra el servidor
    }
    await closeDatabase(); // Cierra la conexión a MongoDB
  });

  it("Debe retornar un mensaje en la ruta principal", async () => {
    const response = await request(app).get("/");
    expect(response.statusCode).toBe(200);
    expect(response.text).toBe("¡Bienvenido a TRIVO AI!");
  });
});
