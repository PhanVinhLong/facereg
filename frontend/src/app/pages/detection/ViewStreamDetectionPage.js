
import React, { useRef } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import { Input, Select } from "../../../_metronic/_partials/controls";
import { useHistory, useParams } from 'react-router-dom';
import ReactHlsPlayer from 'react-hls-player';

import axios from 'axios';
import { BACKEND_URL } from '../../../config';

import { Card, CardHeader, CardBody, CardHeaderToolbar } from "../../../_metronic/_partials/controls";

import detectionAPI from "../../utils/DetectionAPI";

const user = JSON.parse(localStorage.getItem('user'));

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
    marginTop: theme.spacing(3),
  },
  paper: {
    width: '100%',
    marginBottom: theme.spacing(2),
  },
}));

const detectionTypes = ['Image', 'Video', 'Stream'];

export function ViewStreamDetectionPage() {

  const history = useHistory();
  const params = useParams();

  const classes = useStyles();

  const btnRef = useRef();
  const ref = useRef(null);

  const [detection, setDetection] = React.useState([]);
  const [models, setModels] = React.useState([]);
  const [useCustomUrl, setUseCustomUrl] = React.useState(true);

  const DetectionEditSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, "Minimum 2 symbols")
      .max(50, "Maximum 50 symbols")
      .required("Name is required"),
    ori_url: Yup.string()
      .matches(useCustomUrl ? '(?<url>(?:rtmp|http):\S*)' : '[\s\S]*', 'Streaming URL must be RTMP url.')
  });

  React.useEffect(() => {
    async function fetchData() {
      const result = await axios(`${BACKEND_URL}/models`);
      setModels(result.data);

      const result2 = await detectionAPI.getDetectionById(params.id);
      setDetection({
        ...result2.data,
        hls_ori_url: 'http://34.87.117.103:8080/hls/' + result2.data.ori_url.replace('rtmp://34.87.117.103:1935/live/', '') + '.m3u8',
        hls_res_url: 'http://34.87.117.103:8080/hls/' + result2.data.res_url.replace('rtmp://34.87.117.103:1935/live/', '') + '.m3u8'
      });
      console.log(result2.data)
      console.log('http://34.87.117.103:8080/hls/' + result2.data.res_url.replace('rtmp://34.87.117.103:1935/live/', '') + '.m3u8')
    }
    fetchData();
  }, []);

  const initialValues = {
    "name": "",
    "detection_type": "Stream",
    "model_id": 1,
    "description": "",
    "ori_url": "",
    "res_url": "",
    ...detection
  }

  const disabledForm = true;

  return (
    <div className={classes.root}>
      <Card>
        <CardHeader title={`View Stream Detection ${detection.name}`}>
          <CardHeaderToolbar>
            <button
              type="button"
              className="btn btn-light"
              onClick={() => {
                history.push('/detection');
              }}
            >
              <i className="fa fa-arrow-left"></i>
            Back
          </button>
            {`  `}
            {detection.status != 'Done' && <button
              type="button"
              className="btn btn-danger"
              onClick={() => {
                detectionAPI.editDetection(detection.id, { status: 'Done' })
                  .then(response => {
                    if (response.status == 200)
                      setDetection({ ...detection, status: 'Done' })
                  })
              }}
            >
              <i className="glyphicon glyphicon-stop"></i>
            Stop Detecting
          </button>}
            {/* {`  `}
            <button className="btn btn-light ml-2" onClick={() => {
              ref.current.resetForm(initialValues)
            }}>
              <i className="fa fa-redo"></i>
            Reset
          </button>
            {`  `}
            <button
              type="submit"
              onClick={() => {
                if (btnRef && btnRef.current) {
                  btnRef.current.click();
                  // console.log(ref.current)
                }
              }}
              className="btn btn-primary ml-2"
            >
              Save
          </button> */}
          </CardHeaderToolbar>
        </CardHeader>
        <CardBody>
          <Formik
            innerRef={ref}
            enableReinitialize={true}
            initialValues={initialValues}
            validationSchema={DetectionEditSchema}
            onSubmit={(values) => {
              values = {
                ...values,
                created_time: new Date().toISOString(),
                created_by: user.id,
                status: 'Pending'
              };
              // detectionAPI.createDetection(values)
              //   .then(response => {
              //     if (response.status >= 200 && response.status < 300) {
              //       console.log(response)

              //       alert('New detection created successful.');
              //       history.push(`/detection/${response.data.id}`);
              //       history.go();
              //     } else {
              //       alert('Error status ' + String(response.status));
              //       history.push('/detection/');
              //       history.go();
              //     }
              //   });
            }}
          >
            {({ handleSubmit, setFieldValue }) => (
              <>
                <Form className="form form-label-right">
                  <div className="form-group row">
                    <div className="col-lg-4">
                      <Field
                        name="name"
                        component={Input}
                        placeholder="Name"
                        label="Name"
                        disabled={disabledForm}
                      />
                    </div>
                    <div className="col-lg-4">
                      <Select name="detection_type" label="Detection Type" disabled>
                        {detectionTypes.map((dtype) => (
                          <option key={dtype} value={dtype}>
                            {dtype}
                          </option>
                        ))}
                      </Select>
                    </div>
                    <div className="col-lg-4">
                      <Select name="model_id" label="Model" disabled={disabledForm}>
                        {models.map((model) => (
                          <option key={model.id} value={model.name}>
                            {model.name}
                          </option>
                        ))}
                      </Select>
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Description</label>
                    <Field
                      name="description"
                      as="textarea"
                      className="form-control"
                      disabled={disabledForm}
                    />
                  </div>
                  {/* <div className="form-group row">
                    <div className="col-lg-4">
                      <FormControlLabel
                        control={
                          <Switch
                            checked={useCustomUrl}
                            onChange={() => {
                              setUseCustomUrl(!useCustomUrl);
                              setFieldValue('ori_url', '');
                            }}
                            color="primary"
                          />
                        }
                        label="Use custom streaming URL"
                      />
                    </div>
                  </div> */}
                  <div className="form-group row">
                    <div className="col">
                      <Field
                        name="ori_url"
                        component={Input}
                        placeholder="Streaming URL"
                        label="Request Streaming URL"
                        disabled={disabledForm}
                      />
                    </div>
                    <div className="col">
                      <Field
                        name="res_url"
                        component={Input}
                        placeholder="Streaming URL"
                        label="Result Streaming URL"
                        disabled={disabledForm}
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    ref={btnRef}
                    style={{ display: "none" }}
                    onSubmit={() => handleSubmit()}
                  ></button>
                </Form>
                {/* <div className="row">
                  <label className="col">Original</label>
                  <label className="col">Result</label>
                </div> */}
                <div className="row">
                  {/* <div className="text-center col">
                    <ReactHlsPlayer
                      className="img-thumbnail"
                      url={detection.hls_ori_url}
                      autoplay={true}
                      controls={true}
                      width="auto"
                      hlsConfig={{
                        autoStartLoad: true
                      }}
                    />
                  </div>
                  {` `} */}
                  {detection.status != 'Done' &&
                    <div className="text-center col">
                        <ReactHlsPlayer
                          className="img-thumbnail"
                          url={detection.hls_res_url}
                          autoplay={true}
                          controls={true}
                          width="70%"
                          hlsConfig={{
                          autoStartLoad: true
                        }}
                      />
                    </div>}
                </div>
              </>
            )}
          </Formik>
        </CardBody>
      </Card>
    </div>
  );
}