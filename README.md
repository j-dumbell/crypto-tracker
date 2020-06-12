# crypto-tracker

To start (seeded) db and server
`docker-compose up --build db web`

To manually seed (test suite automatically handles seeding)
`python3 -m app.seeding`

To run test_suite
`docker-compose up --build --exit-code-from test`
