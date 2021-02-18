import axios from 'axios';

const token = localStorage.getItem('token');
// const config = {
//   headers: {
//     'Authorization': `Bearer ${token}`
//   }
// };

const detectionAPI = {
  createDetection: (newDetection) => {

    let bodyFormData = new FormData();
    for (var key in newDetection) {
      bodyFormData.append(key, newDetection[key]);
    }

    return axios({
      method: 'post',
      url: '/api/v1/detections',
      data: bodyFormData,
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
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
