import decodeJwt from 'jwt-decode';
import axios from 'axios';

const authProvider = {
  login: (username, password) => {
    let formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const request = new Request('/api/token', {
      method: 'POST',
      body: formData,
    });
    return fetch(request)
      .then((response) => {
        if (response.status < 200 || response.status >= 300) {
          throw new Error(response.statusText);
        }
        return response.json();
      })
      .then(({ access_token }) => {
        const decodedToken = decodeJwt(access_token);
        if (decodedToken.permissions !== 'admin') {
          throw new Error('Forbidden');
        }
        localStorage.setItem('token', access_token);
        localStorage.setItem('permissions', decodedToken.permissions);

        const URL = "/api/v1/users/me";

        let config = {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        };

        axios.get(URL, config).then((response) =>
          localStorage.setItem('user', JSON.stringify(response.data)))

        return Promise.resolve(access_token);
      });
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('permissions');
    localStorage.removeItem('user');
    return Promise.resolve();
  },
  checkError: (error) => {
    const status = error.status;
    if (status === 401 || status === 403) {
      localStorage.removeItem('token');
      return Promise.reject();
    }
    return Promise.resolve();
  },
  checkAuth: () =>
    localStorage.getItem('token') ? Promise.resolve() : Promise.reject(),
  getPermissions: () => {
    const role = localStorage.getItem('permissions');
    return role ? Promise.resolve(role) : Promise.reject();
    // localStorage.getItem('token') ? Promise.resolve() : Promise.reject(),
  },
  getCurrentUser: () => {
    const URL = "192.168.20.152:8000/api/v1/users/me";
    const token = localStorage.getItem('token');
    if (!token) return Promise.reject();

    let config = {
      headers: {
        Authorization: token,
      }
    }

    axios.post(URL, {}, config).then((response) =>
      console.log(response))
  },
};

export default authProvider;
