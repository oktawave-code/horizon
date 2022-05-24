# Oktawave Horizon

Oktawave Horizon is a real time data stream processing platform.

## Flow

Flow represents whole data stream processing process. It is composed of three modules - collector, processor and emitter.

![Flow schema](/assets/flow-schema.png)

### Collector

Collects and stores input data. Additionaly, provides sophisticated routing rules for different data isolation.


### Processor 

Processes data from collector module. Provides two types of processing engines - container images and Apache Flink.

#### Processor - Container images

Container images processor allows to upload one or many user custom container images into the Flow.

![Custom processor schema](/assets/custom-processor-schema.png)


### Processor - Apache Flink

This processor type uses Apache Flink for data processing. User must upload it's own implementation of stream processing process or use Visual Processor Editor

![Flink processor schema](/assets/flink-processor-schema.png)


##### Visual Processor Editor

It is a web application allowing to visually design and deploy complex runtimes for Apache Flink.

![Visual flink editor architecture](/assets/visual-flink-editor-architecture.png)

### Emitter 

All the processed data are stored in emitter module. It serves the data over HTTP protocol for further viewing and processing.
