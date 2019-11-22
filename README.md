# Ceng435 - Term Project 1

### Data Communication and Networking

#### Requirements

- python version must be >= 3.6

- ntplib
- matplotlib

We added ntplib in this project. You can use it without needing any additional download.

## What does this code do? How to run?

### 1) Finds Round-trip time (RTT) costs across the links in the topology.

- **1.1** Open 5 ssh connection for each node.
- **1.2** Copy corresponding files in discoveryScripts into nodes. i.e. s.py to s node, r1.py to r1 node.
- **1.3** Run ConfigureR1.sh, ConfigureR2.sh in r1 and r2, respectively. (Given by instructor.)
  - in node r1
    ```bash
    ./ConfigureR1.sh
    ```
  - in node r2
    ```bash
    ./ConfigureR2.sh
    ```
- **1.4** Now we are ready to discover RTTs. Run scripts in the order s, r1, r2, r3, d.
- - in s node
    ```bash
    python3 s.py
    ```
  - in r1 node
    ```bash
    python3 r1.py
    ```
  - in r2 node
    ```bash
    python3 r2.py
    ```
  - in r3 node
    ```bash
    python3 r3.py
    ```
  - in d node
    ```bash
    python3 d.py
    ```
  - the order is important because they work as:

    - **1.4.1**: d sends a byte to r1, r2 and r3; r3 sends a byte to s and r2; r2 sends a byte to s and r1; r1 sends a byte to r1,
      indicating that they are ready to receive messages.
      Each node except d is responsible for message sending, starts sending after receiving ready-state byte.
    - **1.4.2**: For each interface, there exists a thread in corresponding nodes. We used links as one-way message sending links (and acknowledgments are sent in reverse way)

      - Receiver threads listens link and once they receive message, returns acknowledgement. Sender threads, sends a message and waits till acknowledgement is received. After acknowledgement received, they calculate RTT and continue with the next message.

      - How they calculate RTT?

        - Sender puts timestamp to packet and receiver forward back the timestamp to sender in acknowledgement message. After, sender subtract the timestamp from current time to find RTT.

      - S sends calculated RTTs to corresponding nodes(r1, r2, r3)
      - R1, r2 and r3 writes all costs to link_costs.txt.
      - This flow requires the execution order of s, r1, r2, r3, d.

* **1.5** Read link_cost.txt files from r1, r2 and r3 and we found RTT of each link.You can read cost in r1, r2 and r3 as follows
  ```bash
  cat link_costs.txt
  ```

### 2) Finds end to end delay in s-r3-d in three experiment.

- **2.1** Open 3 ssh connection for s, r3 and d.
- **2.2** Copy corresponding files in experimentScripts into nodes. i.e. s.py to s node and r3.py to r3 node.

- **2.3** For each experiment `i` do:

  - **2.3.1** copy bash scripts from experiment`{i}` file to corresponding node. i.e. experiment1/s.sh to s node.

  - **2.3.2** run bash scripts. It changes the current delay of links. As it is clearly stated, it changes delay, not adds. The node has to have a configured delay. If you will run this code in a clean topology you need to change all the 'change' keyword in the bash scripts to 'add'.

    - in s node
      ```bash
      ./s.sh
      ```
    - in r3 node
      ```bash
      ./r3.sh
      ```
    - in d node
      ```bash
      ./d.sh
      ```

  - **2.3.3** run s.py in s node, run r3.py in r3 node, run d.py in d node.

    - in s node
      ```bash
      python3 s.py
      ```
    - in r3 node
      ```bash
      python3 r3.py
      ```
    - in d node
      ```bash
      python3 d.py
      ```

    * Note: Since s will wait till r3 is ready and r3 will wait till d is ready, running order must be s, r3, d.

  - **2.3.4** d.py prints the 95% confidence interval of end to end delay between s and d nodes in the d node.

    - How? How d.py calculates the 95% confidence interval of end to end delay? Who told it?
      - We told it to do. Same mechanism works here as the one in discovery. S waits acknowledgement to send next message. In the s.py, it gets synchronized time from ntp server via ntplib, puts it to packet and sends packet to r3. r3 directly forwards it to d and d, also, gets synchronized time from ntp server via ntplib and subtracts the one came in packet which s sent from coming from ntp server to find end to end delay of the message. Stores them in a list, calculates mean, standard deviation and confidence interval after last message is received.

We found shortest path by applying dijkstra algorithm to link costs found in first part. It was s - r3 - d. That was the reason we used only these three nodes in the experiment part. However, it can be applied to any other route by changing ips in the scripts and delay configurations.
