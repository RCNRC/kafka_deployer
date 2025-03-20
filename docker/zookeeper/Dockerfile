FROM eclipse-temurin:17-jdk-jammy
ARG ZOOKEEPER_VERSION=3.7.1
RUN apt-get update && apt-get install -y wget
RUN wget https://downloads.apache.org/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz && \
    tar -xzf apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz && \
    mv apache-zookeeper-${ZOOKEEPER_VERSION}-bin /opt/zookeeper
COPY configs/zookeeper.properties /opt/zookeeper/conf/
EXPOSE 2181 2888 3888
VOLUME ["/data"]
CMD ["/opt/zookeeper/bin/zkServer.sh", "start-foreground"]
