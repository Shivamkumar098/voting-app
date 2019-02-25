# Voting-Application
A BlockChain application implementing a Voting System using Sawtooth Framework 



## Instructions for setting up and running the application

1. Build the necessary components used by the application using docker-compose.yaml file by running  : 
   ##### >>&nbsp; docker-compose up
   in the application directory and make necessary changes in the docker-compose.yaml file for further customisation
   <hr>
2. The following operations are currently supported in the application :
    ##### 1. Voting for a party
    ##### 2. Adding a party to blockchain
    ##### 3. Geting the number of votes obtained by the party<br>
    <hr>
    
3. Run the client.py file which requires python3 installed as shown below inside the container voting-client :    
    ##### >>&nbsp;python client.py *(add [party name] or list [party name] or vote [party name] [username])*<br>
    or<br>
    ##### >>&nbsp;docker exec -it voting-client python client.py *(add [party name] or list [party name] or vote [party name] [username])*
    from the terminal
<hr>
