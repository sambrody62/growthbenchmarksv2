import { firebase } from "./Firebase";

const GET_METHOD = "GET";
const POST_METHOD = "POST";

const get = (url) => {
  return fetchWrapper(GET_METHOD, url);
};

const post = (url, data) => {
  return fetchWrapper(POST_METHOD, url, data);
};

const fetchWrapper = async (method, url, data) => {
  const controller = new AbortController();
  const fetchContoller = setTimeout(() => {
    controller.abort();
  }, 30000);

  const currentUser = firebase.auth().currentUser;
  let idToken;
  if (currentUser) {
    idToken = await currentUser.getIdToken(true);
  }
  const headers = { "Content-Type": "application/json" };
  if (idToken) {
    headers.Authorization = `Bearer ${idToken}`;
  }

  let body;
  if (data) {
    body = JSON.stringify(data);
  }

  url =
    (process.env.NODE_ENV === "production"
      ? "https://api.growthbenchmarks.com"
      : "") + url;

  const result = await fetch(url, {
    method,
    headers,
    body,
    signal: controller.signal,
  }).catch((fetchError) => {
    if (fetchError.name === "AbortError") {
      throw new Error("Timeout Error");
    }
    throw fetchError;
  });
  clearTimeout(fetchContoller);
  return result;
};

export default { get, post };
