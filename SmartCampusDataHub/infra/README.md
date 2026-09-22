# Infrastructure for the Smart Campus Data Engineering Upgrade

This folder contains the foundational messaging and state services for the next architecture step:

- Kafka for campus event streaming
- Redis for pipeline state and counters
- No Spark or producers are implemented here yet
- Existing ETL, SQLite, and React frontend remain in place and unchanged

## Files

- docker-compose.yml: Kafka and Redis services
- .env.example: configuration template for environment variables

## Configuration

Create a local .env file from the example before starting the stack:

```powershell
Copy-Item infra\.env.example infra\.env
```

Then adjust the values if needed, especially the Redis password.

## Windows / Docker Desktop commands

Start the infrastructure:

```powershell
docker compose -f infra/docker-compose.yml up -d
```

Stop the infrastructure:

```powershell
docker compose -f infra/docker-compose.yml down
```

## Kafka status

Check the service health and logs:

```powershell
docker compose -f infra/docker-compose.yml ps
```

Or inspect broker health:

```powershell
docker compose -f infra/docker-compose.yml logs kafka --tail 50
```

## Kafka topics

List the topics in the Kafka broker:

```powershell
docker compose -f infra/docker-compose.yml exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list
```

Create the required topics if they are not present:

```powershell
docker compose -f infra/docker-compose.yml exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic campus.students --partitions 3 --replication-factor 1
docker compose -f infra/docker-compose.yml exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic campus.attendance --partitions 3 --replication-factor 1
docker compose -f infra/docker-compose.yml exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic campus.academics --partitions 3 --replication-factor 1
docker compose -f infra/docker-compose.yml exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic campus.events --partitions 3 --replication-factor 1
docker compose -f infra/docker-compose.yml exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic campus.transportation --partitions 3 --replication-factor 1
docker compose -f infra/docker-compose.yml exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic campus.facilities --partitions 3 --replication-factor 1
```

## Redis status

Check Redis health:

```powershell
docker compose -f infra/docker-compose.yml exec redis redis-cli -a campusredispass ping
```

Check Redis service status:

```powershell
docker compose -f infra/docker-compose.yml ps redis
```

## Required Kafka topics

The broker is configured for the following topics:

- campus.students
- campus.attendance
- campus.academics
- campus.events
- campus.transportation
- campus.facilities

Redis is reserved for operational metadata only:

- pipeline status
- current pipeline stage
- records received
- records processed
- records rejected
- pipeline start time
- pipeline completion time

Redis is not used as the underlying campus data store.

## Notes

- Kafka runs in KRaft mode, so no separate Zookeeper service is required.
- The legacy CSV ETL pipeline and SQLite database remain available as the fallback path while the new infrastructure foundation is introduced.
