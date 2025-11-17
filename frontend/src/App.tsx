import { useState } from "react";

interface CROBreakdown {
  title: number;
  meta_description: number;
  h1_tags: number;
  ctas: number;
  forms: number;
  content: number;
}

interface PerformanceMetrics {
  load_time_ms: number;
  dom_content_loaded_ms: number;
  page_size_kb: number | null;
  performance_score: number;
}

interface CROAnalysis {
  url: string;
  score: number;
  breakdown: CROBreakdown;
  recommendations: string[];
  performance?: PerformanceMetrics;
}

interface ComparisonResult {
  url: string;
  score: number;
  breakdown: CROBreakdown;
  performance: PerformanceMetrics;
  rank: number;
}

interface ComparisonAnalysis {
  timestamp: string;
  total_analyzed: number;
  results: ComparisonResult[];
  winner: Record<string, string>;
  insights: string[];
}

function App() {
  const [mode, setMode] = useState<"single" | "compare">("single");
  const [url, setUrl] = useState("");
  const [compareUrls, setCompareUrls] = useState(["", "", ""]);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<CROAnalysis | null>(null);
  const [comparison, setComparison] = useState<ComparisonAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);
    setAnalysis(null);
    setComparison(null);

    try {
      const response = await fetch(
        "http://localhost:8000/api/cro/recommendations",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to analyze URL");
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleCompareSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validUrls = compareUrls.filter((u) => u.trim() !== "");

    if (validUrls.length < 2) {
      setError("Please provide at least 2 URLs for comparison");
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);
    setComparison(null);

    try {
      const response = await fetch("http://localhost:8000/api/cro/compare", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ urls: validUrls }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to compare URLs");
      }

      const data = await response.json();
      setComparison(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const addCompareUrl = () => {
    if (compareUrls.length < 10) {
      setCompareUrls([...compareUrls, ""]);
    }
  };

  const removeCompareUrl = (index: number) => {
    if (compareUrls.length > 2) {
      setCompareUrls(compareUrls.filter((_, i) => i !== index));
    }
  };

  const updateCompareUrl = (index: number, value: string) => {
    const newUrls = [...compareUrls];
    newUrls[index] = value;
    setCompareUrls(newUrls);
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return "text-green-600";
    if (score >= 50) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 75) return "bg-green-100 border-green-300";
    if (score >= 50) return "bg-yellow-100 border-yellow-300";
    return "bg-red-100 border-red-300";
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `#${rank}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
      <div className="w-full max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-3 bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">
            CRO Analyzer Pro
          </h1>
          <p className="text-gray-600 text-lg">
            AI-powered conversion optimization & competitor comparison
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="flex justify-center mb-6">
          <div className="bg-white rounded-lg shadow-md p-1 inline-flex">
            <button
              onClick={() => setMode("single")}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                mode === "single"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-gray-600 hover:text-gray-800"
              }`}
            >
              Single Analysis
            </button>
            <button
              onClick={() => setMode("compare")}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                mode === "compare"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-gray-600 hover:text-gray-800"
              }`}
            >
              Compare Competitors
            </button>
          </div>
        </div>

        {/* Single Analysis Form */}
        {mode === "single" && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label
                  htmlFor="url"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Website URL
                </label>
                <input
                  id="url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 placeholder-gray-400"
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:from-indigo-400 disabled:to-purple-400 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:hover:scale-100 shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Analyzing...
                  </span>
                ) : (
                  "🚀 Analyze Website"
                )}
              </button>
            </form>
          </div>
        )}

        {/* Comparison Form */}
        {mode === "compare" && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <form onSubmit={handleCompareSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Competitor URLs (2-10)
                </label>
                <div className="space-y-3">
                  {compareUrls.map((url, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="url"
                        value={url}
                        onChange={(e) => updateCompareUrl(index, e.target.value)}
                        placeholder={`https://competitor${index + 1}.com`}
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 placeholder-gray-400"
                        disabled={loading}
                      />
                      {compareUrls.length > 2 && (
                        <button
                          type="button"
                          onClick={() => removeCompareUrl(index)}
                          className="px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                          disabled={loading}
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                </div>
                {compareUrls.length < 10 && (
                  <button
                    type="button"
                    onClick={addCompareUrl}
                    className="mt-3 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    disabled={loading}
                  >
                    + Add URL
                  </button>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:from-indigo-400 disabled:to-purple-400 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:hover:scale-100 shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Comparing...
                  </span>
                ) : (
                  "⚔️ Compare Competitors"
                )}
              </button>
            </form>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <span className="text-2xl">❌</span>
              <div>
                <h3 className="text-lg font-semibold text-red-800 mb-1">
                  Error
                </h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Single Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Score Display */}
            <div
              className={`rounded-2xl p-8 border-2 ${getScoreBgColor(
                analysis.score
              )} shadow-lg`}
            >
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  CRO Score
                </h2>
                <div
                  className={`text-7xl font-bold ${getScoreColor(
                    analysis.score
                  )}`}
                >
                  {analysis.score}
                  <span className="text-4xl">/100</span>
                </div>
                <p className="mt-4 text-gray-600">
                  {analysis.score >= 75
                    ? "🎉 Excellent conversion optimization!"
                    : analysis.score >= 50
                    ? "👍 Good, but room for improvement"
                    : "⚠️ Needs significant improvements"}
                </p>
              </div>
            </div>

            {/* Performance Metrics */}
            {analysis.performance && (
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  <span>⚡</span> Performance Metrics
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                    <div className="text-sm font-medium text-blue-700 mb-1">
                      Load Time
                    </div>
                    <div className="text-2xl font-bold text-blue-900">
                      {(analysis.performance.load_time_ms / 1000).toFixed(2)}s
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                    <div className="text-sm font-medium text-green-700 mb-1">
                      DOM Content Loaded
                    </div>
                    <div className="text-2xl font-bold text-green-900">
                      {(analysis.performance.dom_content_loaded_ms / 1000).toFixed(2)}s
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                    <div className="text-sm font-medium text-purple-700 mb-1">
                      Page Size
                    </div>
                    <div className="text-2xl font-bold text-purple-900">
                      {analysis.performance.page_size_kb
                        ? `${analysis.performance.page_size_kb.toFixed(0)}KB`
                        : "N/A"}
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-4 border border-amber-200">
                    <div className="text-sm font-medium text-amber-700 mb-1">
                      Performance Score
                    </div>
                    <div className={`text-2xl font-bold ${getScoreColor(analysis.performance.performance_score)}`}>
                      {analysis.performance.performance_score}/100
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Breakdown */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Score Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(analysis.breakdown).map(([key, value]) => {
                  const maxScores: Record<string, number> = {
                    title: 20,
                    meta_description: 15,
                    h1_tags: 15,
                    ctas: 25,
                    forms: 15,
                    content: 10,
                  };
                  const maxScore = maxScores[key] || 0;
                  const percentage = (value / maxScore) * 100;

                  return (
                    <div
                      key={key}
                      className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                    >
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-semibold text-gray-700 capitalize">
                          {key.replace(/_/g, " ")}
                        </span>
                        <span className="font-bold text-indigo-600">
                          {value}/{maxScore}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Recommendations */}
            {analysis.recommendations.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-6">
                  Recommendations
                </h3>
                <div className="space-y-3">
                  {analysis.recommendations.map((recommendation, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200"
                    >
                      <span className="text-blue-600 font-bold text-lg">
                        {index + 1}.
                      </span>
                      <p className="text-gray-700 flex-1">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Comparison Results */}
        {comparison && (
          <div className="space-y-6">
            {/* Insights */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl shadow-lg p-8 border-2 border-indigo-200">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <span>💡</span> Competitive Insights
              </h3>
              <div className="space-y-3">
                {comparison.insights.map((insight, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-white rounded-lg border border-indigo-200"
                  >
                    <p className="text-gray-700">{insight}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Comparison Table */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Competitor Rankings
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        Rank
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">
                        URL
                      </th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">
                        CRO Score
                      </th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">
                        Performance
                      </th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">
                        Load Time
                      </th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">
                        Page Size
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.results.map((result) => (
                      <tr
                        key={result.url}
                        className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                          result.rank === 1 ? "bg-yellow-50" : ""
                        }`}
                      >
                        <td className="py-4 px-4">
                          <span className="text-2xl">
                            {getRankBadge(result.rank)}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-indigo-600 hover:underline text-sm font-medium"
                          >
                            {new URL(result.url).hostname}
                          </a>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span
                            className={`font-bold text-lg ${getScoreColor(
                              result.score
                            )}`}
                          >
                            {result.score}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span
                            className={`font-bold text-lg ${getScoreColor(
                              result.performance.performance_score
                            )}`}
                          >
                            {result.performance.performance_score}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center text-gray-700">
                          {(result.performance.load_time_ms / 1000).toFixed(2)}s
                        </td>
                        <td className="py-4 px-4 text-center text-gray-700">
                          {result.performance.page_size_kb
                            ? `${result.performance.page_size_kb.toFixed(0)}KB`
                            : "N/A"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Winners by Category */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                Category Winners 🏆
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(comparison.winner).map(([category, url]) => (
                  <div
                    key={category}
                    className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-lg p-4 border-2 border-amber-200"
                  >
                    <div className="text-sm font-semibold text-amber-700 mb-1 uppercase tracking-wide">
                      {category.replace(/_/g, " ")}
                    </div>
                    <div className="text-sm text-amber-900 font-medium truncate">
                      {new URL(url).hostname}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="text-center mt-8 text-gray-500 text-sm">
          Powered by AI • FastAPI • React • Playwright • Performance Analytics
        </div>
      </div>
    </div>
  );
}

export default App;
