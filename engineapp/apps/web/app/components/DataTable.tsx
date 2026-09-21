type Row = Record<string, string | number>;

export function DataTable({ rows, caption }: { rows: Row[]; caption?: string }) {
  if (!rows.length) return <p>No rows.</p>;
  const cols = Object.keys(rows[0]);
  return (
    <table>
      {caption && <caption>{caption}</caption>}
      <thead>
        <tr>
          {cols.map((c) => (
            <th key={c} scope="col">{c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>
            {cols.map((c) => (
              <td key={c} className={typeof r[c] === "number" ? "num" : undefined}>
                {typeof r[c] === "number" ? r[c].toLocaleString() : String(r[c]).replace(/_/g, " ")}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
