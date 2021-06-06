import axios from 'axios';

const token = localStorage.getItem('token');
// const config = {
//   headers: {
//     'Authorization': `Bearer ${token}`
//   }
// };

const detectionAPI = {
  getDetections: () => {
    return axios.get(
      `/api/v1/detections`,
      {
        headers: {
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

  getDetectionById: (detection_id) => {
    return axios.get(
      `/api/v1/detections/${detection_id}`,
      {
        headers: {
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
  createDetection: (newDetection) => {
    console.log(newDetection)

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
  createFacereg: (url, images) => {

    let bodyFormData = new FormData();
    for (let i = 0; i < images.length; i++) {
      bodyFormData.append("files", images[i]);
    }

    return axios({
      method: 'post',
      url: '/api/v1/faces/upload?url=' + url,
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
  editDetection: (detectionId, updateDetection) => {
    return axios({
      method: 'post',
      url: `/api/v1/detections/${detectionId}`,
      data: updateDetection,
      headers: {
        'Content-Type': 'application/json',
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

  createStreamDetection: (newDetection) => {

    let bodyFormData = new FormData();
    for (var key in newDetection) {
      bodyFormData.append(key, newDetection[key]);
    }

    return axios({
      method: 'post',
      url: '/api/v1/detections/stream',
      data: bodyFormData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
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
