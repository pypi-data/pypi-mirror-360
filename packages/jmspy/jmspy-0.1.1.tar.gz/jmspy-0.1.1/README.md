# Jmspy — A Native Python JMS OpenWire Client for ActiveMQ using Jpype

Welcome to Jmspy, a simple tool that enables Python applications to communicate with an Apache ActiveMQ broker using the native JMS OpenWire protocol — not STOMP.
Unlike other solutions that rely on STOMP (Simple Text Oriented Messaging Protocol) or Jython (Python-in-Java), 
this client is built using JPype, which provides a bridge between the JVM and Python via JNI (Java Native Interface). 
This allows Python to directly interact with JMS-compliant JAR libraries in a proper JVM process — 
the same way Java applications would.
By default, OpenWire listens on port 61616.

---

## Features

- Native JMS (OpenWire) protocol support
- Pure Python interface, no STOMP
- Uses standard Java JARs with JPype
- Send/receive binary files via queues
- Easy integration with Apache ActiveMQ

---

## Installation

You can use the module directly from this repository by downloading it manually or via pip:

    pip install jmspy

The required JAR files are already included in the libs/ subfolder for convenience.
If you prefer to fetch your own versions of the dependencies, you may use Maven:

    mvn clean package

---

## Usage Example

    import jmspy
    with jmspy.Jmspy("tcp://localhost:61616") as mq:
        mq.send_file("myQueue", "message1.txt")
        mq.receive_file("myQueue")

You can optionally specify a save directory:

    mq.receive_file("myQueue", save_dir="downloads/")

---

## Architecture Notes

- This project uses JPype to launch a local JVM inside the Python process.
- It interacts directly with the jakarta.jms interfaces.
- It is focused on native OpenWire/JMS messaging — for developers who need the full fidelity of a JMS client in Python.

---

## JAR Dependencies

The following JARs are included in the libs/ folder:

- activemq-all-6.1.7.jar
- jakarta.jms-api-3.1.0.jar
- log4j-api-2.25.0.jar
- log4j-core-2.25.0.jar

Feel free to update them to newer versions as needed.

---

## Requirements

- Python 3.8+
- Java 11 or newer (Java 17+ recommended for better JPype support)
- JPype 1.4.1+ (pip install jpype1)

---

## Contribution

Contributions, suggestions, or improvements are welcome! 

---

## License

This project is released under the MIT License.

