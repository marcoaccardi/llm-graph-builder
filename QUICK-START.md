BACKEND
backend && source .venv/bin/activate && uvicorn score:app --reload --host 0.0.0.0 --port 8000


NEO4J local db
neo4j-community-5.26.0
wget https://dist.neo4j.org/neo4j-community-5.26.0-unix.tar.gz
tar -xzf neo4j-community-5.26.0-unix.tar.gz && echo "Neo4j
      5.26.0 extracted successfully"

make sure neo4j.conf is configured for local usage

 ./bin/neo4j start
 ./bin/neo4j stop

 It is available at http://localhost:7474


FRONTEND
npm run dev

OLLAMA
ollama serve
