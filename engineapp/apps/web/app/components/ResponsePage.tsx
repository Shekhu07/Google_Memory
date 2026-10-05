import Link from "next/link";

type Option = { option: string; count: number; ids: string[] };
type Answer = { id: string; text: string };
type Question = {
  q: string;
  kind: "choice" | "multi" | "scale" | "text";
  answered: number;
  options?: Option[];
  answers?: Answer[];
};
export type ResponseData = {
  n: number;
  first: string;
  last: string;
  sections: { title: string; questions: Question[] }[];
};

const KIND_LABEL: Record<Question["kind"], string> = {
  choice: "Pick one",
  multi: "Tick all that apply",
  scale: "Scale 1–5",
  text: "Free text",
};

function fmt(d: string) {
  const [y, m, day] = d.split("-").map(Number);
  const month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1];
  return `${day} ${month} ${y}`;
}

export function ResponsePage({
  data,
  eyebrow,
  title,
  lead,
  csvHref,
  idRange,
  other,
}: {
  data: ResponseData;
  eyebrow: string;
  title: string;
  lead: React.ReactNode;
  csvHref: string;
  idRange: string;
  other: { href: string; label: string };
}) {
  let num = 0;
  return (
    <main className="shell">
      <header className="topbar">
        <h2>
          <Link href="/" className="rp-back">
            ← Discovery Engine
          </Link>
        </h2>
        <nav>
          <Link href={other.href}>{other.label}</Link>
        </nav>
      </header>

      <div className="prose">
        <p className="t-eyebrow">{eyebrow}</p>
        <h1 className="t-page">{title}</h1>
        <p className="hero-lead">{lead}</p>
      </div>

      <div className="rp-facts">
        <span><strong>{data.n}</strong> responses</span>
        <span>{fmt(data.first)} – {fmt(data.last)}</span>
        <span>Respondents {idRange}</span>
        <a href={csvHref} download>Download all responses (CSV)</a>
      </div>
      <p className="t-support rp-note">
        The Google Form is closed, so this page shows every question exactly as it was asked, with every
        answer. Anonymised: contact details removed, timestamps cut to the date. Answer options nobody chose
        are not listed.
      </p>

      {data.sections.map((s) => (
        <section key={s.title} className="rp-section">
          <h3 className="t-section">{s.title}</h3>
          {s.questions.map((q) => {
            num += 1;
            return (
              <article key={q.q} className="rp-q">
                <div className="rp-q-head">
                  <span className="rp-num">Q{num}</span>
                  <h4>{q.q}</h4>
                </div>
                <p className="rp-meta">
                  {KIND_LABEL[q.kind]} · answered by {q.answered} of {data.n}
                </p>
                {q.answered === 0 && <p className="t-support">No one answered this optional question.</p>}
                {q.options && q.options.length > 0 && (
                  <ul className="rp-options">
                    {q.options.map((o) => (
                      <li key={o.option}>
                        <div className="rp-opt-row">
                          <span className="rp-opt">{q.kind === "scale" ? `${o.option} / 5` : o.option}</span>
                          <span className="rp-count">{o.count}</span>
                        </div>
                        <div className="rp-bar" aria-hidden="true">
                          <span style={{ width: `${(o.count / q.answered) * 100}%` }} />
                        </div>
                        <span className="rp-ids">{o.ids.join(" · ")}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {q.answers && q.answers.length > 0 && (
                  <ul className="rp-text">
                    {q.answers.map((a) => (
                      <li key={a.id}>
                        <span className="rp-id">{a.id}</span>
                        <span>&ldquo;{a.text}&rdquo;</span>
                      </li>
                    ))}
                  </ul>
                )}
              </article>
            );
          })}
        </section>
      ))}
    </main>
  );
}
