import React, { useState, useEffect } from "react";
import { sendMessageToBot, getChatHistory, closeChatroom } from "../api/chat";
import styled from "styled-components";
import Webcam from "react-webcam";

// 날짜를 원하는 형식으로 변환하는 함수
const formatDate = (date) => {
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const year = date.getFullYear();
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

const ChatBox = styled.div`
  width: 100%;
  max-width: 430px;
  border: 2px solid #eeeeee;
  border-radius: 15px;
  background-color: white;
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);
  margin-top: 20px;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: rgb(244, 244, 244);
  padding: 10px;
  font-size: 18px;
  border-bottom: 4px solid white;
`;

const ChatHistory = styled.div`
  padding: 20px;
  height: 450px;
  overflow-y: auto;
  scrollbar-width: thin;
  &::-webkit-scrollbar {
    display: block;
  }
`;

const MessageContainer = styled.div`
  display: flex;
  width: 100%;
  justify-content: ${({ isUser }) => (isUser ? "flex-end" : "flex-start")};
  margin-bottom: 10px;
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 10px;
  border-radius: 10px;
  font-size: 14px;
  background: ${({ isUser }) => (isUser ? "#a3cafa" : "#fbe4f5")};
  color: ${({ isUser }) => (isUser ? "white" : "black")};
  word-wrap: break-word;
  text-align: left;
`;

const InputContainer = styled.div`
  display: flex;
  padding: 10px;
  background-color: rgb(241, 241, 241);
`;

const Input = styled.input`
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 5px;
  background-color: ${({ disabled }) => (disabled ? "#f1f1f1" : "white")};
  color: ${({ disabled }) => (disabled ? "#ccc" : "black")};
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "text")};
`;

const Button = styled.button`
  margin-left: 5px;
  padding: 10px;
  background-color: ${({ disabled }) => (disabled ? "#cccccc" : "#A3C6ED")};
  color: ${({ disabled }) => (disabled ? "#999" : "white")};
  border: none;
  border-radius: 5px;
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
`;

const EndButton = styled.button`
  margin-left: 5px;
  padding: 10px;
  background-color: ${({ disabled }) => (disabled ? "#cccccc" : "#dc3545")};
  color: ${({ disabled }) => (disabled ? "#999" : "white")};
  border: none;
  border-radius: 5px;
  cursor: ${({ disabled }) => (disabled ? "not-allowed" : "pointer")};
`;

const WebcamContainer = styled.div`
  width: 50%;
  max-width: 430px;
  margin-bottom: 20px;
  border-radius: 15px;
  background-color: black;
  height: 200px; // 웹캠 화면 크기 설정
  display: flex;
  justify-content: center;
  align-items: center;
`;

const ChatRoomDetail = ({ userId, chatroomId, setSelectedChatroom }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [conversationEnd, setConversationEnd] = useState(false);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const { chats, conversationEnd: endStatus } = await getChatHistory(
          chatroomId
        );
        console.log("채팅 내역 API 응답:", chats);
        setMessages(chats);
        setConversationEnd(endStatus);
      } catch (error) {
        console.error("채팅 내역을 가져오는 데 실패했습니다:", error);
      }
    };

    fetchMessages();
  }, [chatroomId]);

  const sendMessage = async () => {
    if (!input.trim() || conversationEnd) return; // 대화 종료된 상태에서는 메시지 전송 불가

    const userMessage = {
      user_id: userId,
      user_message: input,
      bot_response: "응답 대기 중...",
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const botResponse = await sendMessageToBot(chatroomId, input);
      setMessages((prev) =>
        prev.map((msg, index) =>
          index === prev.length - 1
            ? { ...msg, bot_response: botResponse }
            : msg
        )
      );
    } catch (error) {
      console.error("메시지 전송 실패:", error);
    }
  };

  // 대화 종료 처리
  const handleEndConversation = async () => {
    try {
      const response = await closeChatroom(chatroomId);
      console.log("대화 종료 API 응답:", response);
      if (response) {
        setConversationEnd(true);
        alert("대화가 종료되었습니다.");
        setSelectedChatroom(null);
      }
    } catch (error) {
      console.error("대화 종료 실패:", error);
    }
  };

  // 날짜를 가져오기 위해 chatroomId 대신 Date를 사용하여 포맷
  const chatroomDate = new Date();
  const formattedDate = formatDate(chatroomDate);

  return (
    <div>
      <ChatBox>
        <ChatHeader>
          <button onClick={() => setSelectedChatroom(null)}>← 뒤로</button>
          <span style={{ marginLeft: "55px" }}>내 친구</span>
          <span style={{ fontSize: "15px" }}>{formattedDate}</span>
        </ChatHeader>

        <ChatHistory>
          {messages.length > 0 ? (
            messages.map((msg, index) => (
              <React.Fragment key={index}>
                {msg.user_message && (
                  <MessageContainer isUser={true}>
                    <MessageBubble isUser={true}>
                      {msg.user_message}
                    </MessageBubble>
                  </MessageContainer>
                )}
                {msg.bot_response && (
                  <MessageContainer isUser={false}>
                    <MessageBubble isUser={false}>
                      {msg.bot_response}
                    </MessageBubble>
                  </MessageContainer>
                )}
              </React.Fragment>
            ))
          ) : (
            <p>채팅 내역이 없습니다.</p>
          )}
        </ChatHistory>
        <InputContainer>
          <Input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="메시지를 입력하세요..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            disabled={conversationEnd} // 대화 종료 시 입력창 비활성화
          />

          <Button onClick={sendMessage} disabled={conversationEnd}>
            전송
          </Button>
        </InputContainer>
        <InputContainer>
          <EndButton onClick={handleEndConversation} disabled={conversationEnd}>
            대화 종료하기
          </EndButton>
        </InputContainer>
      </ChatBox>
      {/* 웹캠 화면 */}
      <WebcamContainer
        style={{
          backgroundColor: "transparent", // 배경을 투명하게 설정
        }}
      >
        <Webcam
          audio={false}
          screenshotFormat="image/jpeg"
          width="100%"
          videoConstraints={{
            facingMode: "user",
          }}
          style={{
            opacity: 0, // 웹캠을 화면에 보이지 않게 설정
          }}
        />
      </WebcamContainer>
    </div>
  );
};

export default ChatRoomDetail;
