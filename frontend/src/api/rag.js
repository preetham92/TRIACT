export async function askRag(query, jwtToken) {
  const resp = await fetch("http://localhost:8011/api/rag/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${jwtToken}`
    },
    body: JSON.stringify({ query })
  });
  return await resp.json();
}
