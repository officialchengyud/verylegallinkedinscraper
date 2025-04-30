import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
} from "react";
import {
  Timestamp,
  doc,
  updateDoc,
  arrayUnion,
  getDoc,
} from "firebase/firestore";
import { db } from "../main";
import { useAuth } from "./AuthContext";

interface ChatMessage {
  role: string;
  message: string;
  timestamp: Timestamp;
}

interface ChatContextType {
  chatLog: ChatMessage[];
  getChat: () => void;
  sendChat: (message: string) => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const [chatLog, setChatLog] = useState<ChatMessage[]>([]);

  const getChat = async () => {
    if (user) {
      const docRef = doc(db, "chats", user.uid);
      const docSnap = await getDoc(docRef);
      const messages = docSnap.exists() ? docSnap.data().messages : [];
      setChatLog(messages ?? []);
    }
  };

  useEffect(() => {
    if (user) {
      getChat();
    }
  }, [user]);

  const sendChat = async (message: string) => {
    if (user) {
      const newMessage = {
        role: "user",
        message,
        timestamp: Timestamp.now(),
      };
      const docRef = doc(db, "chats", user.uid);
      await updateDoc(docRef, {
        messages: arrayUnion(newMessage),
      });
      setChatLog((chats) => [...chats, newMessage]);
    }
  };

  return (
    <ChatContext.Provider value={{ chatLog, getChat, sendChat }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
