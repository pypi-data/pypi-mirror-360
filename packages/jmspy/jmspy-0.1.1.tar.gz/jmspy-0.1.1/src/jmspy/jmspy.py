#!/usr/bin/env python3
"""
Install requiremnts: pip install -r requirements.txt
Use "mvn clean package" to below libraries or download JARs any version you like. You need to have:
  https://repo1.maven.org/maven2/org/apache/activemq/activemq-all/6.1.7/
  https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-api/2.25.0/
  https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.25.0/
  https://repo1.maven.org/maven2/jakarta/jms/jakarta.jms-api/3.1.0/jakarta.jms-api-3.1.0.jar
Notes:  
 If you get "javax.jms.BytesMessage" you have to replace javax.jms to jakarta.jms after change in JEE8
 You can find latest version here: https://github.com/Tomasz-Malewski License: MIT enjoy
"""
import os
import logging
import jpype
import re


class Jmspy:
    """
    A Jpype class using native JAR AMQ Openwire to send/receive messages from ActiveMQ broker. It's not a STOMP.
    """

    def __init__(self, connection_string: str = "tcp://127.0.0.1:61616"):
        """
        Init amqpy class with default values
        :param connection_string: The connection string for the ActiveMQ broker example tcp://127.0.0.1:61616.
        """
        self.connection = None
        self.connection_string = connection_string
        here = os.path.dirname(os.path.abspath(__file__))
        JAR_PATHS = [
         os.path.join(here, "libs", "activemq-all-6.1.7.jar"),
         os.path.join(here, "libs", "log4j-api-2.25.0.jar"),
         os.path.join(here, "libs", "log4j-core-2.25.0.jar"),
         os.path.join(here, "libs", "jakarta.jms-api-3.1.0.jar"),
         ]
        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath(
                # for JVM 17+ to avoid warnings
            ), "--enable-native-access=ALL-UNNAMED", classpath=JAR_PATHS)
        connection_factory = jpype.JClass(
            "org.apache.activemq.ActiveMQConnectionFactory")
        bytes_message = jpype.JClass("jakarta.jms.BytesMessage")
        try:
            factory = connection_factory(self.connection_string)
            self.connection = factory.createConnection()
            self.connection.start()
        except Exception as error:
            logging.error(f"Error connecting to ActiveMQ: {error}")
            

    def send_file(self, queue, filename):
        """
        Send a file to the specified queue in ActiveMQ
        :param queue: The name of the queue to send the file to.
        :param filename: The path to the file to send.
        :return: True if the file was sent successfully, False otherwise.
        """
        if not os.path.isfile(filename):
            logging.error(f"File does not exist: {filename}")
            return False
        assert self.connection is not None, "Connection to ActiveMQ is not established."
        session = self.connection.createSession(
            False, jpype.JClass("jakarta.jms.Session").AUTO_ACKNOWLEDGE)
        destination = session.createQueue(queue)
        producer = session.createProducer(destination)
        with open(filename, "rb") as f:
            data = f.read()
        message = session.createBytesMessage()
        message.writeBytes(data)
        try:
            producer.send(message)
            logging.info(f"File sent {queue}/{filename}")
            return True
        except exception as error:
            logging.error(
                f"Error sending file {filename} to queue {queue} - {error}")
            return False
        finally:
            if producer:
                producer.close()
            if session:
                session.close()
        return False

    def receive_file(self, queue, save_dir=".", timeout=500):
        """
        Receive a file from the specified queue in ActiveMQ and save it to the given directory.
        :param queue: Name of the queue to receive from.
        :param save_dir: Directory to save the received file default local.
        :param timeout: Timeout in milliseconds for receiving message.
        """
        session = None
        consumer = None
        try:
            session = self.connection.createSession(
                False,
                jpype.JClass("jakarta.jms.Session").AUTO_ACKNOWLEDGE
            )
            destination = session.createQueue(queue)
            consumer = session.createConsumer(destination)
            message = consumer.receive(timeout)
            if message is None:
                logging.info(
                    f"No message received from queue '{queue}' within timeout.")
                return False
            property_names = message.getPropertyNames()
            headers = []
            jms_id = message.getJMSMessageID()
            while property_names.hasMoreElements():
                key = property_names.nextElement()
                value = message.getObjectProperty(key)
                print(key, value)
                headers.append(f"{key}: {value}")
            logging.info(
                f"Received message {jms_id} with custom headers:\n" + "\n".join(headers))            
            # we have to sanitize filename to match filesystem rules
            filename = re.sub(r'[^A-Za-z0-9._-]', '_', str(jms_id))
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)        
            # if not jpype.isInstanceOf(message, jpype.JClass("jakarta.jms.BytesMessage")): # There is no isInstanceOf
            bytes_message = jpype.JClass("jakarta.jms.BytesMessage")
            if not isinstance(message, bytes_message):
                logging.error(
                    f"Received message is not BytesMessage on queue '{queue}'.")
                return False
            length = int(message.getBodyLength())
            java_buffer = jpype.JArray(jpype.JByte)(length)
            read_bytes = message.readBytes(java_buffer)
            data = bytes(java_buffer[:read_bytes])
            with open(save_path, "wb") as f:
                f.write(data)
            logging.info(f"File received and saved as: {save_path} size {length} bytes")
            return True
        except Exception as e:
            logging.error(
                f"Failed to receive file from queue '{queue}'. Error: {e}")
            return False
        finally:
            if consumer:
                consumer.close()
            if session:
                session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Clean up connection and shutdown JVM
        :return: None
        """
        if self.connection:
            self.connection.close()
        jpype.shutdownJVM()



if __name__ == "__main__":
    pass
    logging.basicConfig(level=logging.DEBUG)
    with Jmspy("tcp://localhost:61616") as mq:
        pass
        mq.send_file("myQueue", "example.txt")
        mq.receive_file("myQueue", save_dir=".")
