import axios from "axios";

export const LOGIN_URL = "http://192.168.20.152:8000/api/token";
export const REGISTER_URL = "api/auth/register";
export const REQUEST_PASSWORD_URL = "api/auth/forgot-password";

export const ME_URL = "http://192.168.20.152:8000/api/v1/users/me";

const config = {
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
}

export function login(username, password) {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)
  return axios.post(LOGIN_URL, params, config);
}

export function register(email, fullname, username, password) {
  return axios.post(REGISTER_URL, { email, fullname, username, password });
}

export function requestPassword(email) {
  return axios.post(REQUEST_PASSWORD_URL, { email });
}

export function getUserByToken() {
  // Authorization head should be fulfilled in interceptor.
  return axios.get(ME_URL);
}
