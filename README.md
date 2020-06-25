# crypto-tracker
API and daily prices etl for the crypto-tracker project

To start (seeded) db and server
`docker-compose up --build db web`

To manually seed (test suite automatically handles seeding)
`python3 -m app.seeding`

To run test suite
`docker-compose up --build --exit-code-from test`
