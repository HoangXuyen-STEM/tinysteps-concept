// The three message pillars from the campaign messaging house. Wording avoids
// "mất gốc" everywhere — the audience is professional teachers and the framing is
// rebuilding a foundation, never a deficiency.
const pillars = [
  {
    icon: "🧱",
    title: "Đúng phần bạn đang thiếu",
    body: "Nhiều lộ trình tiếng Anh giả định bạn đã có sẵn vốn từ và ngữ pháp nền. Ai chưa chắc phần đó sẽ thấy đuối ngay tuần đầu. TinySteps xây đúng phần móng ấy, để bạn học tiếp ở bất cứ đâu cũng nhẹ và vững hơn.",
  },
  {
    icon: "⏱️",
    title: "Vừa sức, mỗi ngày một bước",
    body: "Bài ngắn, có hình minh họa và âm thanh. Hệ thống ôn tập ngắt quãng tự nhắc lại đúng những từ bạn sắp quên, nên bạn không cần tự soạn kế hoạch học. 10-15 phút mỗi ngày, vừa với lịch dạy và chấm bài.",
  },
  {
    icon: "🎯",
    title: "Lộ trình rõ ràng tới A2 - B1",
    body: "Năm cấp độ theo khung Cambridge quen thuộc với giáo viên: Starters, Movers, Flyers, KET, PET. Bạn luôn biết mình đang ở đâu và bước tiếp theo là gì.",
  },
] as const;

export function LandingPillars() {
  return (
    <section className="mx-auto mt-16 max-w-3xl px-4 sm:px-6">
      <h2 className="text-2xl font-bold text-slate-900">Vì sao TinySteps hợp với giáo viên</h2>
      <div className="mt-6 space-y-4">
        {pillars.map(({ icon, title, body }) => (
          <div
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            key={title}
          >
            <p className="text-2xl leading-none" aria-hidden="true">
              {icon}
            </p>
            <h3 className="mt-3 text-lg font-bold text-slate-900">{title}</h3>
            <p className="mt-2 leading-relaxed text-slate-600">{body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
