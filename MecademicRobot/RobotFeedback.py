import socket
import re

class RobotFeedback:
    """Class for the Mecademic Robot allowing for live positional 
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
        cartesian: tuple of floats
            the cartesian values in mm and degrees of the TRF
        version: str
            firmware version of the Mecademic Robot
    """

    def __init__(self, address, firmware_version):
        """Constructor for an instance of the Class Mecademic Robot 

        Parameters
        --------
        address: str 
            The IP address associated to the Mecademic Robot
        """
        self.address = address
        self.socket = None
        self.robotstatus =()
        self.gripperstatus =()
        self.joints = ()    #Joint Angles, angles in degrees | [theta_1, theta_2, ... theta_n]
        self.cartesian = () #Cartesian coordinates, distances in mm, angles in degrees | [x,y,z,alpha,beta,gamma]
        self.jointsvel =()  
        self.torque =()
        self.accelerometer =()
        self.last_msg_chunk = ''
        a = re.search(r'(\d+)\.(\d+)\.(\d+)', firmware_version)
        self.version = a.group(0)
        self.version_regex = [int(a.group(1)), int(a.group(2)), int(a.group(3))]

    def Connect(self):
        """Connects Mecademic Robot object communication to the physical Mecademic Robot

        Returns
        --------
        status: boolean 
            Return whether the connection is established
        """
        try:
            self.socket = socket.socket()                   #Get a socket
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)
            self.socket.settimeout(1)                     #set the timeout to 100ms
            try:
                self.socket.connect((self.address, 10001))  #connect to the robot's address
            except socket.timeout:                          #catch if the robot is not connected to in time
                raise TimeoutError                          
            # Receive confirmation of connection
            if self.socket is None:                         #check that socket is not connected to nothing
                raise RuntimeError
            self.socket.settimeout(1)                       #set timeout to 1 seconds
            try:
                if(self.version_regex[0] <= 7):
                    self.getData()
                elif(self.version_regex[0] > 7):              #RobotStatus and GripperStatus are sent on 10001 upon connecting from 8.x firmware
                    msg = self.socket.recv(256).decode("ascii")   #read message from robot            
                    self._getRobotStatus(msg)
                    self._getGripperStatus(msg)
                return True
            except socket.timeout:
                raise RuntimeError
        except TimeoutError:
            return False
        # OTHER USER !!!
        except RuntimeError:
            return False
    
    def Disconnect(self):
        """Disconnects Mecademic Robot object from physical Mecademic Robot
        """
        if(self.socket is not None):
            self.socket.close()
            self.socket = None        

    def getData(self,delay=0.1):
        """Receives message from the Mecademic Robot and 
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
            raw_msg = self.socket.recv(256).decode("ascii")         #read message from robot
            raw_response = raw_msg.split("\x00")                    # Split the data at \x00 to manage fragmented data
            raw_response[0] = self.last_msg_chunk + raw_response[0] # Merge the first data with last fragment from previous data stream
            self.last_msg_chunk = raw_response[-1]
                
            for response in raw_response[:-1]:
                if(self.version_regex[0] <= 7):
                    self._getJoints(response)
                    self._getCartesian(response)
                    
                elif(self.version_regex[0] > 7):
                    self._getJoints(response)
                    self._getCartesian(response)
                    self._getJointsVel(response)
                    self._getTorqueRatio(response)
                    self._getAccelerometer(response)
            
        except TimeoutError:                
            pass

    def _getRobotStatus(self,response):
        """
        Gets the values of RobotStatus bits from the message sent by the Robot upon connecting
        Values saved to attribute robotstatus of the object

        Parameters
        --------
        response: str
            message received from the Robot
        
        """
        code = None
        code = self._getResponseCode('RobotStatus')
        for resp_code in code:
            if response.find(resp_code) != -1:
                self.robotstatus = self._decodeMsg(response,resp_code)

    def _getGripperStatus(self,response):
        """
        Gets the values of GripperStatus bits from the message sent by the Robot upon connecting
        Values saved to attribute robotstatus of the object

        Parameters
        --------
        response: str
            message received from the Robot
        
        """

        code = None
        code = self._getResponseCode('GripperStatus')
        for resp_code in code:
            if response.find(resp_code) != -1:
                self.gripperstatus = self._decodeMsg(response,resp_code)
        
    def _getJoints(self, response):
        """Gets the joint values of the variables from the message sent by the Robot.
        Values saved to attribute joints of the object.

        Parameters
        --------
        response: str
            message received from the Robot
        """
        code = None
        code = self._getResponseCode('JointsPose')
        
        for resp_code in code:
            if response.find(resp_code) != -1:
                self.joints = self._decodeMsg(response,resp_code)
    
    def _getCartesian(self, response):
        """Gets the cartesian values of the variables from the message sent by the Robot.
        Values saved to attribute cartesian of the object.

        Parameters
        --------
        response: str
            message received from the Robot
        """
        
        code = None
        code = self._getResponseCode('CartesianPose')
        
        for resp_code in code:
            if response.find(resp_code) != -1:
                self.cartesian = self._decodeMsg(response,resp_code)

    def _getJointsVel(self,response):
        """Gets the velocity values of the Joints from the message sent by the Robot.
        Values saved to attribute jointsvel of the object.

        Parameters
        --------
        response: str
            message received from the Robot
        """
        
        code = None
        code = self._getResponseCode('JointsVel')
        for resp_code in code:
            if response.find(resp_code) != -1:
                self.jointsvel = self._decodeMsg(response,resp_code)
        
    def _getTorqueRatio(self,response):
        """Gets the torque ratio values of the Joints from the message sent by the Robot.
        Values saved to attribute torque of the object.

        Parameters
        --------
        response: str
            message received from the Robot
        """
        
        code = None
        code = self._getResponseCode('TorqueRatio')
        for resp_code in code:
            if response.find(resp_code) != -1:
                self.torque = self._decodeMsg(response,resp_code)
    
    def _getAccelerometer(self,response):
        """Gets the accelerometers values from the message sent by the Robot.
        Values saved to attribute accelerometer of the object.

        Parameters
        --------
        response: str
            message received from the Robot
        """
        
        code = None
        code = self._getResponseCode('AccelerometerData')
        for resp_code in code:
            if response.find(resp_code) != -1:
                self.accelerometer = self._decodeMsg(response,resp_code)

    def _getResponseCode(self,param):
        """ Retreives the response code for the parameters being streamed on port 100001
        Parameters
        --------
        param: str
            parameter that needs to be extracted from raw data strem from Mecademic Robot
            1. Robot Status {sent only once upon connecting on 10001}
            2. Gripper Status {sent only once upon connecting on 10001}
            3. Joints Pose feedback
            4. Cartesian Pose feedback
            5. Joints Velocity feedback
            6. Torque Ratio
            7. Accelerometer data

        Returns
        --------
        answer_list: list of strings
            list of response codes to search for in the raw data stream
        """
        if param.find('RobotStatus') != -1:
            return ["[2007]"]
        elif param.find('GripperStatus')!= -1:
            return ["[2079]"]
        
        elif param.find('JointsPose') != -1:
            if(self.version_regex[0] <= 7):
                return ["[2102]"]
            elif(self.version_regex[0] > 7):
                return ["[2026]","[2210]"]
            
        elif  param.find('CartesianPose') != -1:
            if(self.version_regex[0] <= 7):
                return ["[2103]"]
            elif(self.version_regex[0] > 7):
                return ["[2027]","[2211]"]
            
        elif param.find('JointsVel') != -1:
            return ["[2212]"]
        elif param.find('TorqueRatio') != -1:
            return ["[2213]"]
        elif param.find('AccelerometerData') != -1:
            return ["[2220]"]
        else:
            return ["Invalid"]

    def _decodeMsg(self,response,resp_code):
        response = response.replace(resp_code+"[","").replace("]","")
        params =()
        if response != '':
            param_str = response.split(',')
            if len(param_str) == 6:
                params = tuple((float(x) for x in param_str))
            elif len(param_str) == 7:
                params = tuple((float(x) for x in param_str[1:]))   # remove timestamp
            else:
                params =()

        return params
                    
            
