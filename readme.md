# Ceng435 - Term Project 2
## Who we are?
##### Beste Burhan 2171395
##### Kürşat Öztürk 2171874

### Data Communication and Networking

#### Requirements

- python version must be >= 3.6

- matplotlib



## What does this code do? How to run?

### 1) Reliable Data Transferring Utilized with Pipelining and Multi-Home.

- **1.1** Open 5 ssh connection for each node.
- **1.2** Copy corresponding files in discoveryScripts into nodes. Use the bash script we provided.
        ```
            ./deploy_scripts.sh 
        ``` 
- **1.3** Add delay to the links.

    ```bash
    tc qdisc change dev [INTERFACE] root netem loss 5% delay 3ms
    ```
    ```bash
    tc qdisc change dev [INTERFACE] root netem loss 15% delay 3ms
    ```
    ```bash
    tc qdisc change dev [INTERFACE] root netem loss 38% delay 3ms 
    ```

- **1.4** Now we are ready to deliver file. Run scripts by ensuring s is the last one that starts running.
- - in s node
    ```bash
    python3 script.py ${EXPERIMENT}
    ```
  - in r1 node
    ```bash
    python3 script.py
    ```
  - in r2 node
    ```bash
    python3 script.py
    ```
  - in r3 node
    ```bash
    python3 script.py
    ```
  - in d node
    ```bash
    python3 script.py ${EXPERIMENT}
    ```
  - EXPERIMENT parameter determines which experiment to run. If it is 1, first experiment will be conducted. If 2, second experiment will be conducted. Make sure that source and destination starts with same EXPERIMENT parameter. Otherwise, destination will not listen the routers source sends the packets. 
  - the start of execution time of s is important because they work as:

    - **1.4.1**: d starts and waits for upcoming packets, each router starts and waits for upcoming packets but s starts and starts sending packets. If noone is listening, it would end up sending packets to emptiness. Although our implementation covers the scenario that d starts after s, it would not be beneficial because we are timing the execution time of s. It would extend the execution time.
    - **1.4.2**: Source script is thread oriented. Meaning that it may end up running 200+ thread. Make sure that there is no high workload on machine.  

      - S sends packet to required link and starts a timeout thread for the packet. After timeout passed, the thread checks if packet is acknowledged. If packet is not acknowledged it resends it.
      - R1, r2 and r3 gets the packets and forwards it. Flow is always either s->router->d or d->router->s. 

* **1.5** Check the file integrity.
  ```bash
    diff input.txt output${EXPERIMENT}
  ```
  - again EXPERIMENT is the same with the above. It should not print any output. 

