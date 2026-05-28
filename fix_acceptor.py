import time
import quickfix as fix

class AcceptorApplication(fix.Application):
    """
    The Acceptor acts as the Broker/Exchange.
    It receives orders and handles execution messages.
    """
    def onCreate(self, sessionID): 
        print(f"[Acceptor] Session created: {sessionID}")
        
    def onLogon(self, sessionID): 
        print(f"\n[Acceptor] CLIENT LOGGED ON SUCCESSFULLY! Session: {sessionID}\n")
        
    def onLogout(self, sessionID): 
        print(f"\n[Acceptor] Client Logged Out / Disconnected. Session: {sessionID}\n")
        
    def toAdmin(self, message, sessionID): pass
    def toApp(self, message, sessionID): pass
    def fromAdmin(self, message, sessionID): pass

    def fromApp(self, message, sessionID):
        """
        This callback triggers automatically whenever an application message 
        (like a New Order) arrives from the client.
        """
        print("-" * 50)
        print(f"[Acceptor] Received Application Message!")
        
        msg_type = fix.MsgType()
        message.getHeader().getField(msg_type)
        
        if msg_type.getValue() == fix.MsgType_NewOrderSingle:
            symbol = fix.Symbol()
            side = fix.Side()
            quantity = fix.OrderQty()
            cl_ord_id = fix.ClOrdID()
            
            message.getField(symbol)
            message.getField(side)
            message.getField(quantity)
            message.getField(cl_ord_id)
            
            side_str = "BUY" if side.getValue() == fix.Side_BUY else "SELL"
            
            print(f"  » Message Type: New Order Single (35=D)")
            print(f"  » Client Order ID: {cl_ord_id.getValue()}")
            print(f"  » Ticker Symbol: {symbol.getValue()}")
            print(f"  » Order Side: {side_str}")
            print(f"  » Order Quantity: {quantity.getValue()}")
        else:
            print(f"  » Unknown message type: {msg_type.getValue()}")
        print("-" * 50)

def main():
    try:

        settings = fix.SessionSettings("config/acceptor.cfg")
        application = AcceptorApplication()
        store_factory = fix.FileStoreFactory(settings)
        log_factory = fix.FileLogFactory(settings)
        
        acceptor = fix.SocketAcceptor(application, store_factory, settings, log_factory)
        
        print("[Acceptor] Starting FIX server application...")
        acceptor.start()
        print("[Acceptor] Server is listening on port specified in config (5001)...")
        
        # main process running
        while True:
            time.sleep(1)
            
    except (fix.ConfigError, fix.RuntimeError) as e:
        print(f"QuickFIX Error: {e}")
    except KeyboardInterrupt:
        print("[Acceptor] Shutting down server...")
        acceptor.stop()

if __name__ == "__main__":
    main()
