import { offer, formatVnd, currentPriceVnd } from "@/lib/marketing/offer";

// Answers the five objections that come up most, in the buyer's own words. Kept as
// plain <details> so it works without JavaScript on the low-end phones many teachers use.
const faqs = [
  {
    q: "Ngoài kia có nhiều app miễn phí, tôi còn cần TinySteps không?",
    a: "TinySteps không cạnh tranh về số lượng bài tập. Nó tập trung vào phần móng — vốn từ và ngữ pháp nền — sắp theo đúng thứ tự và tự nhắc lại đúng từ bạn sắp quên. Học 10 phút mỗi sáng, bạn thật sự nhớ và dùng được, chứ không chỉ 'đã học cho có'.",
  },
  {
    q: "Tôi mất căn bản từ lâu, bắt đầu lại có kịp không?",
    a: "Starters bắt đầu từ những từ đầu tiên, có hình và có âm thanh, thiết kế đúng cho người học lại từ đầu. Tôi cũng bắt đầu từ đó, ở tuổi ngoài 40.",
  },
  {
    q: "Tôi bận lắm, có theo nổi không?",
    a: "10-15 phút mỗi ngày là đủ. Ứng dụng tự nhắc lại đúng từ bạn sắp quên nên bạn không phải tự soạn kế hoạch hay nhớ hôm nay học gì.",
  },
  {
    q: "Chuyển khoản cho cá nhân, tôi hơi ngại.",
    a: `Hoàn toàn hiểu. Vì vậy có ba điều: bạn học thử 3 bài miễn phí trước khi trả đồng nào; tôi công khai tên thật và nơi công tác; và nếu không ưng, hoàn tiền trong ${offer.refundDays} ngày, không cần lý do.`,
  },
  {
    q: `${formatVnd(currentPriceVnd())} là trả một lần hay hằng tháng?`,
    a: "Một lần duy nhất, học trọn đời cả 5 cấp độ. Không gia hạn, không phí ẩn, không cần thẻ tín dụng.",
  },
] as const;

export function LandingFaq() {
  return (
    <section className="mx-auto mt-16 max-w-3xl px-4 sm:px-6">
      <h2 className="text-2xl font-bold text-slate-900">Câu hỏi thường gặp</h2>
      <div className="mt-6 space-y-3">
        {faqs.map(({ q, a }) => (
          <details
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            key={q}
          >
            <summary className="cursor-pointer font-semibold text-slate-900">{q}</summary>
            <p className="mt-3 leading-relaxed text-slate-600">{a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
