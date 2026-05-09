"use client";

import { useEffect, useState } from "react";
import type { GraphData, GraphNode, DocBundle } from "@/lib/types";
import { styleFor } from "@/lib/colors";

interface Props {
  data: GraphData;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onClose: () => void;
}

export default function DetailPanel({ data, selectedId, onSelect, onClose }: Props) {
  const node = selectedId ? data.nodes.find((n) => n.id === selectedId) ?? null : null;
  const [bundle, setBundle] = useState<DocBundle | null>(null);
  const [bundleLoading, setBundleLoading] = useState(false);

  useEffect(() => {
    if (!node || node.kind !== "document") {
      setBundle(null);
      return;
    }
    setBundleLoading(true);
    fetch(`/docs/${node.id}.json`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j: DocBundle | null) => setBundle(j))
      .catch(() => setBundle(null))
      .finally(() => setBundleLoading(false));
  }, [node]);

  if (!node) return null;

  // Find connected nodes (incoming + outgoing) for context
  const connections = data.edges
    .filter((e) => e.source === node.id || e.target === node.id)
    .map((e) => {
      const otherId = e.source === node.id ? e.target : e.source;
      const other = data.nodes.find((n) => n.id === otherId);
      return { other, role: e.role, kind: e.kind };
    })
    .filter((c) => c.other) as { other: GraphNode; role?: string; kind: string }[];

  const s = styleFor(node.kind);

  return (
    <aside className="glass fixed top-0 right-0 h-full w-[420px] max-w-[90vw] m-3 flex flex-col z-30">
      <header className="flex items-start gap-3 p-4 border-b border-stroke/40">
        <span
          className="w-3 h-3 rounded-full mt-1.5 shrink-0"
          style={{ background: s.color, boxShadow: `0 0 12px ${s.color}` }}
        />
        <div className="flex-1 min-w-0">
          <div className="text-xs uppercase tracking-wider text-fg-mute">{node.kind}</div>
          <h2 className="text-base font-medium leading-tight break-words">{node.label}</h2>
        </div>
        <button onClick={onClose} className="text-fg-mute hover:text-fg" aria-label="Close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               strokeWidth="2"><path d="M18 6 6 18M6 6l12 12" /></svg>
        </button>
      </header>

      <div className="flex-1 overflow-y-auto scroll-thin p-4 space-y-4">
        <AttrTable attrs={node.attrs} />

        {node.kind === "document" && (
          <DocumentBody node={node} bundle={bundle} loading={bundleLoading} />
        )}

        {connections.length > 0 && (
          <section>
            <h3 className="text-xs uppercase tracking-wider text-fg-mute mb-2">
              Connected ({connections.length})
            </h3>
            <ul className="space-y-1">
              {connections.slice(0, 80).map((c, i) => {
                const cs = styleFor(c.other.kind);
                return (
                  <li key={i}>
                    <button
                      onClick={() => onSelect(c.other.id)}
                      className="w-full text-left px-2 py-1.5 rounded hover:bg-white/[0.05] flex items-center gap-2"
                    >
                      <span
                        className="w-2 h-2 rounded-full shrink-0"
                        style={{ background: cs.color }}
                      />
                      <span className="flex-1 truncate text-sm">{c.other.label}</span>
                      {c.role && <span className="text-xs text-fg-mute">{c.role}</span>}
                    </button>
                  </li>
                );
              })}
            </ul>
          </section>
        )}
      </div>
    </aside>
  );
}

function AttrTable({ attrs }: { attrs: GraphNode["attrs"] }) {
  const entries = Object.entries(attrs).filter(([k]) => k !== "identifier");
  if (!entries.length) return null;
  return (
    <section>
      <h3 className="text-xs uppercase tracking-wider text-fg-mute mb-2">Attributes</h3>
      <dl className="text-sm space-y-1.5">
        {entries.map(([k, v]) => {
          const display = Array.isArray(v) ? v.join(", ") : String(v);
          const isUrl = typeof v === "string" && /^https?:\/\//.test(v);
          return (
            <div key={k} className="grid grid-cols-[7rem_1fr] gap-2">
              <dt className="text-fg-mute font-mono text-xs pt-0.5">{k}</dt>
              <dd className="break-words">
                {isUrl ? (
                  <a href={display} target="_blank" rel="noopener noreferrer"
                     className="text-accent hover:underline break-all">{display}</a>
                ) : (
                  <span className={k === "description" ? "text-sm leading-relaxed" : ""}>{display}</span>
                )}
              </dd>
            </div>
          );
        })}
      </dl>
    </section>
  );
}

function DocumentBody({
  node, bundle, loading,
}: { node: GraphNode; bundle: DocBundle | null; loading: boolean }) {
  const [tab, setTab] = useState<"viewer" | "claims" | "pages">("viewer");

  const filename       = String(node.attrs.filename ?? "");
  const url            = String(node.attrs.url ?? "");
  const shape          = String(node.attrs.shape ?? "");
  const videoEmbedUrl  = String(node.attrs.video_embed_url ?? "");
  const videoDvidsUrl  = String(node.attrs.video_dvids_url ?? "");
  const dvidsId        = String(node.attrs.dvids_id ?? "");

  // Local visual-artifact assets bundled in /public/visual-artifacts/.
  const localAsset = filename ? `/visual-artifacts/${filename}` : "";
  const isPng      = filename.toLowerCase().endsWith(".png");
  const isLocalVid = filename.toLowerCase().match(/\.(mp4|webm|mov)$/);
  const hasLocal   = isPng || (shape === "visual-artifact" && filename.toLowerCase().endsWith(".pdf"));
  const hasVideo   = !!videoEmbedUrl;
  const hasPdf     = url.toLowerCase().endsWith(".pdf") || filename.toLowerCase().endsWith(".pdf");

  return (
    <section className="space-y-3">
      <div className="flex gap-1 text-xs">
        {(["viewer", "claims", "pages"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-2 py-1 rounded ${
              tab === t ? "bg-white/[0.10] text-fg" : "text-fg-mute hover:text-fg"
            }`}
          >
            {t === "viewer" ? "Document"
              : t === "claims" ? `Claims (${bundle?.claims.length ?? 0})`
              : `Pages (${bundle?.pages.length ?? 0})`}
          </button>
        ))}
      </div>

      {tab === "viewer" && (
        <div className="space-y-3">
          {/* DVIDS video embed — for any document with a paired or
              video-only DVIDS record. */}
          {hasVideo && (
            <div className="space-y-1">
              <div className="text-[11px] uppercase tracking-wider text-fg-mute flex items-center gap-2">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z" />
                </svg>
                DVIDS video {dvidsId && `· id ${dvidsId}`}
              </div>
              <div className="aspect-video w-full rounded overflow-hidden border border-stroke/40 bg-black">
                <iframe
                  src={videoEmbedUrl}
                  className="w-full h-full"
                  allow="autoplay; fullscreen; picture-in-picture"
                  allowFullScreen
                  title={`DVIDS ${dvidsId}`}
                />
              </div>
              {videoDvidsUrl && (
                <a href={videoDvidsUrl} target="_blank" rel="noopener noreferrer"
                   className="text-xs text-accent hover:underline">open on dvidshub.net ↗</a>
              )}
            </div>
          )}

          {/* PDF / image / local-file viewer */}
          {(hasPdf || hasLocal) && (
            <div className="space-y-1">
              {hasVideo && (
                <div className="text-[11px] uppercase tracking-wider text-fg-mute">
                  Companion PDF
                </div>
              )}
              {isPng && (
                <img src={localAsset} alt={node.label}
                     className="w-full rounded border border-stroke/40" />
              )}
              {!isPng && isLocalVid && (
                <video src={url} controls className="w-full rounded" />
              )}
              {!isPng && !isLocalVid && hasLocal && (
                <iframe
                  src={localAsset}
                  className="w-full h-[60vh] rounded border border-stroke/40 bg-white"
                  title={node.label}
                />
              )}
              {!isPng && !isLocalVid && !hasLocal && hasPdf && url && (
                <div className="text-sm text-fg-mute leading-relaxed">
                  Hosted on war.gov (Akamai) — open externally:
                  <div className="mt-2">
                    <a href={url} target="_blank" rel="noopener noreferrer"
                       className="text-accent hover:underline break-all">{url}</a>
                  </div>
                </div>
              )}
            </div>
          )}

          {!hasVideo && !hasPdf && !hasLocal && (
            <div className="text-sm text-fg-mute">
              {url
                ? <a href={url} target="_blank" rel="noopener noreferrer"
                     className="text-accent hover:underline break-all">{url}</a>
                : "No file or video link in the manifest."}
            </div>
          )}
        </div>
      )}

      {tab === "claims" && <ClaimsList loading={loading} bundle={bundle} />}
      {tab === "pages"  && <PagesList loading={loading} bundle={bundle} />}
    </section>
  );
}

function ClaimsList({ loading, bundle }: { loading: boolean; bundle: DocBundle | null }) {
  if (loading) return <div className="text-sm text-fg-mute">Loading…</div>;
  if (!bundle || !bundle.claims.length) return <div className="text-sm text-fg-mute">No structured claims for this document.</div>;
  return (
    <ul className="space-y-2">
      {bundle.claims.map((c) => (
        <li key={c.id} className="rounded border border-stroke/40 p-2.5">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs px-1.5 py-0.5 rounded bg-white/[0.06] text-fg-mute">
              {c.kind}
            </span>
            <span className="text-xs text-fg-mute font-mono">{c.method}</span>
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-line">{c.text}</p>
        </li>
      ))}
    </ul>
  );
}

function PagesList({ loading, bundle }: { loading: boolean; bundle: DocBundle | null }) {
  const [open, setOpen] = useState<number | null>(1);
  if (loading) return <div className="text-sm text-fg-mute">Loading…</div>;
  if (!bundle || !bundle.pages.length) return <div className="text-sm text-fg-mute">No OCR pages for this document.</div>;
  return (
    <ul className="space-y-1.5">
      {bundle.pages.map((p) => (
        <li key={p.id} className="rounded border border-stroke/40">
          <button
            onClick={() => setOpen(open === p.page ? null : p.page)}
            className="w-full text-left px-3 py-2 flex items-center justify-between hover:bg-white/[0.04]"
          >
            <span className="text-sm">Page {p.page}</span>
            <span className="text-xs text-fg-mute">{p.text.length} chars</span>
          </button>
          {open === p.page && (
            <pre className="px-3 pb-3 pt-1 text-xs whitespace-pre-wrap break-words text-fg/90 max-h-[40vh] overflow-y-auto scroll-thin">
              {p.text}
            </pre>
          )}
        </li>
      ))}
    </ul>
  );
}
