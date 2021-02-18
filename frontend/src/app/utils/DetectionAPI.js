import decodeJwt from 'jwt-decode';
import axios from 'axios';

const detectionAPI = {
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
};

export default detectionAPI;
