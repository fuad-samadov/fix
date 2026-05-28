import time
import json
import zmq
import quickfix as fix
from datetime import datetime, timezone

class InitiatorApplication(fix.Application):
    """
    Standard QuickFIX Application Callbacks
    """
    def onCreate(self, sessionID): print(f"Session created: {sessionID}")
    def onLogon(self, sessionID): print(f"Logon successful: {sessionID}")
    def onLogout(self, sessionID): print(f"Logout: {sessionID}")
    def toAdmin(self, message, sessionID): pass
    def toApp(self, message, sessionID): pass
    def fromAdmin(self, message, sessionID): pass
    def fromApp(self, message, sessionID): print(f"Received from server: {message}")

    def send_fix_order(self, order_data, session_id):

        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        
        cl_ord_id = f"{int(time.time() * 1000)}-{order_data['symbol']}"
        message.setField(fix.ClOrdID(cl_ord_id))              
        message.setField(fix.Symbol(order_data["symbol"]))    
        side = order_data.get("side", "BUY")
        fix_side = fix.Side_BUY if side == "BUY" else fix.Side_SELL
        message.setField(fix.Side(fix_side))                  
        message.setField(fix.OrderQty(int(order_data["quantity"]))) 
        message.setField(fix.OrdType(fix.OrdType_MARKET))      
        message.setField(fix.TransactTime()) 
        
        fix.Session.sendToTarget(message, session_id)
        print("[Initiator] Sent FIX NewOrderSingle to Acceptor!")

def main():

    settings = fix.SessionSettings("config/initiator.cfg")
    application = InitiatorApplication()
    store_factory = fix.FileStoreFactory(settings)
    log_factory = fix.FileLogFactory(settings)
    initiator = fix.SocketInitiator(application, store_factory, settings, log_factory)
    
    initiator.start()  

    time.sleep(2) # no need anymore ? 
    
    # ZeroMQ PULL Socket to listen to the UI
    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.PULL)
    zmq_socket.bind("tcp://127.0.0.1:5555")
    
    print("[Initiator] Listening for UI commands on port 5555...")
    
    # Listen for local UI commands
    try:
        while True:
            if zmq_socket.poll(timeout=100):
                message_string = zmq_socket.recv_string()
                order_data = json.loads(message_string)
                print(f"[Initiator] Got data from UI: {order_data}")
                
                if order_data.get("action") == "NEW_ORDER":
                    active_sessions = initiator.getSessions()
                    if not active_sessions:
                        print("[Initiator] Error: No active FIX sessions found")
                        continue
                    live_session_id = active_sessions[0]

                    application.send_fix_order(order_data, live_session_id)
    except KeyboardInterrupt:
        initiator.stop()

if __name__ == "__main__":
    main()
