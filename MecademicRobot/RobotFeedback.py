import socket

class RobotFeedback:
    r"""Class for the Mecademic Robot allowing for live positional 
    feedback of the Mecademic Robot 

    Attributes
    --------
        Address: str
            IP Address
        socket: socket
            socket connecting to physical Mecademic Robot
        joints: tuple of floats
            joint angle in degrees of each joint starting from joint 1 going all
            way to joint 6
        pose: tuple of floats
            the pose values in mm and degrees of the TRF
    """
    def __init__(self, address):
        r"""Constructor for an instance of the Class Mecademic Robot 

        Parameters
        --------
        address: str 
            The IP address associated to the Mecademic Robot
        """
        self.address = address
        self.socket = None
        self.joints = ()    #Joint Angles, angles in degrees | [theta_1, theta_2, ... theta_n]
        self.pose = () #Pose coordinates, distances in mm, angles in degrees | [x,y,z,alpha,beta,gamma]

    def Connect(self):
        r"""Connects Mecademic Robot object communication to the physical Mecademic Robot

        Returns
        --------
        status: boolean 
            Return whether the connection is established
        """
        try:
            self.socket = socket.socket()                   #Get a socket
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)
            self.socket.settimeout(0.1)                     #set the timeout to 100ms
            try:
                self.socket.connect((self.address, 10001))  #connect to the robot's address
            except socket.timeout:                          #catch if the robot is not connected to in time
                raise TimeoutError                          
            # Receive confirmation of connection
            if self.socket is None:                         #check that socket is not connected to nothing
                raise RuntimeError
            self.socket.settimeout(1)                       #set timeout to 1 seconds
            try:    
                self.getData()
                return True
            except socket.timeout:
                raise RuntimeError
        except TimeoutError:
            return False
        # OTHER USER !!!
        except RuntimeError:
            return False
    
    def Disconnect(self):
        r"""Disconnects Mecademic Robot object from physical Mecademic Robot
        """
        if(self.socket is not None):
            self.socket.close()
            self.socket = None        

    def getData(self, delay=0.1):
        r"""Receives message from the Mecademic Robot and 
        saves the values in appropriate variables

        Parameters
        --------
        delay: int or float 
            time to set for timeout of the socket
        """
        if self.socket is None:                         #check that the connection is established
            return                                      #if no connection, nothing to receive
        self.socket.settimeout(delay)                   #set read timeout to desired delay
        try:
            response = self.socket.recv(256).decode("ascii")   #read message from robot
            self._getJoints(response)
            self._getPose(response)
        except TimeoutError:                
            pass

    def _getJoints(self, response):
        r"""Gets the joint values of the variables from the message sent by the Robot.
        Values saved to attribute joints of the object.

        Parameters
        --------
        response: str
            message received from the Robot
        """
        start = response.find("[2102]")                         #isolate data from message format
        response = response[start:]
        end = response.find("\x00")
        response = response[:end]
        response = response.replace("[2102][","").replace("]","")
        joints_str = response.split(',')
        self.joints = tuple((float(x) for x in joints_str))      #convert position data to floats
    
    def _getPose(self, response):
        """Gets the pose values of the variables from the message sent by the Robot.
        Values saved to attribute pose of the object.

        Parameters
        --------
        response: str
            message received from the Robot
        """
        start = response.find("[2103]")                         #isolate data from message format
        response = response[start:]
        end = response.find("\x00")
        response = response[:end]
        response = response.replace("[2103][","").replace("]","")
        pose_str = response.split(',')
        self.pose = tuple((float(x) for x in pose_str))      #convert position data to floats
    