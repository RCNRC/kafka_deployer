# Multi-stage build for Kafka
FROM eclipse-temurin:17-jdk-jammy as builder
ARG KAFKA_VERSION=3.2.0
RUN apt-get update && apt-get install -y wget
RUN wget https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_2.13-${KAFKA_VERSION}.tgz && \
    tar -xzf kafka_2.13-${KAFKA_VERSION}.tgz

FROM eclipse-temurin:17-jre-jammy
COPY --from=builder kafka_2.13-${KAFKA_VERSION} /opt/kafka
COPY configs/kafka_server.properties /opt/kafka/config/
EXPOSE 9092 9093
VOLUME ["/data"]
CMD ["/opt/kafka/bin/kafka-server-start.sh", "/opt/kafka/config/kafka_server.properties"]
