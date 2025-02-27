// src/api/diary.js
import api from './config'; 

// 대화방 요약 가져오기
export const getDiarySummary = async (chatroomId) => {
    try {
      const response = await api.post('/diary/summary', { chatroom_id: chatroomId });
      return response.data; 
    } catch (error) {
      console.error("Failed to fetch diary summary", error);
      throw error; 
    }
};
  

// 일기 저장
export const saveDiary = async (userId, content, date, emotion, summary) => {
  try {
    const response = await api.post("/diary/save", {
      user_id: userId,  
      content,    
      date,       
      emotion,    
      summary,   
    });
    return response.data;  
  } catch (error) {
    console.error("Failed to save diary", error);
    throw error; 
  }
};

