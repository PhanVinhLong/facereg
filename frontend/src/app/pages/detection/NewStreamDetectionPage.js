
import React, { useRef } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import { Input, Select } from "../../../_metronic/_partials/controls";
import { useHistory } from 'react-router-dom';

import {
  Switch,
  FormControlLabel
} from "@material-ui/core";

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

export function NewStreamDetectionPage() {

  const history = useHistory();

  const classes = useStyles();

  const btnRef = useRef();
  const ref = useRef(null);

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
    }
    fetchData();
  }, []);

  const initialValues = {
    "name": "",
    "detection_type": "Stream",
    "model_id": 1,
    "description": "",
    "ori_url": ""
  }

  return (
    <div className={classes.root}>
      <Card>
        <CardHeader title="Create New Stream Detection">
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
          </button>
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
              detectionAPI.createStreamDetection(values)
                .then(response => {
                  if (response.status >= 200 && response.status < 300) {
                    console.log(response)

                    alert('New detection created successful.');
                    history.push(`/detection/stream/${response.data.id}`);
                    history.go();
                  } else {
                    alert('Error status ' + String(response.status));
                    history.push('/detection/');
                    history.go();
                  }
                });
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
                      <Select name="model_id" label="Model">
                        {models.map((model) => (
                          <option key={model.id} value={model.id}>
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
                    />
                  </div>
                  <div className="form-group row">
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
                  </div>
                  <div className="form-group row">
                    <div className="col-lg-4">
                      <Field
                        name="ori_url"
                        component={Input}
                        placeholder="Streaming URL"
                        label="Streaming URL"
                        disabled={!useCustomUrl}
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
              </>
            )}
          </Formik>
        </CardBody>
      </Card>
    </div>
  );
}