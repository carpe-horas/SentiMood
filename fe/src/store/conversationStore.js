import { create } from 'zustand';
import { getDiarySummary, saveDiary } from '../api/diary';

const useConversationStore = create((set) => ({
  isConversationEnded: false,
  summary: null,
  setConversationEnded: (status) => set({ isConversationEnded: status }),
  handleConversationEnd: async (chatroomId, userId, emotion) => {
    set({ isConversationEnded: true });
    try {
      console.log("요약 요청 시작...");
      const summaryResponse = await getDiarySummary(chatroomId);
      console.log("요약 결과:", summaryResponse);

      if (!summaryResponse || !summaryResponse.summary) {
        throw new Error("요약 데이터가 비어 있습니다.");
      }

      const summary = summaryResponse.summary;
      set({ summary });

      // 요약이 완료되면 일기 저장 API 호출
      const currentDate = new Date().toISOString();
      console.log("일기 저장 요청 시작...");
      const saveResponse = await saveDiary(userId, summary, currentDate, emotion, summary);
      console.log("일기 저장 결과:", saveResponse);

      if (!saveResponse) {
        throw new Error("일기 저장 실패");
      }
    } catch (error) {
      console.error("요약 처리 중 오류 발생", error);
    }
  },
}));

export default useConversationStore;