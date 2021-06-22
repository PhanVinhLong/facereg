import axios from 'axios';

const token = localStorage.getItem('token');
// const config = {
//   headers: {
//     'Authorization': `Bearer ${token}`
//   }
// };

const detectionAPI = {

  createFacereg: (url, images) => {

    let bodyFormData = new FormData();
    for (let i = 0; i < images.length; i++) {
      bodyFormData.append("files", images[i]);
    }

    return axios({
      method: 'post',
      url: '/api/v1/update_facebank?url=' + url,
      data: bodyFormData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
      .then((response) => {
        if (response.status < 200 || response.status >= 300) {
          throw new Error(response.statusText);
        }
        return Promise.resolve(response);
      })
  },
};

export default detectionAPI;