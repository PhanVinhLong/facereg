
import React, { useRef } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import { Input, Select } from "../../../_metronic/_partials/controls";
import { useHistory } from 'react-router-dom';

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

const FILE_SIZE = 25 * 1024;
const SUPPORTED_FORMATS = [
  "image/jpg",
  "image/jpeg",
  "image/gif",
  "image/png"
];

function requiredWhenDefined() {
  return this.nullable()
    .default({})
    .required();
}

Yup.addMethod(Yup.mixed, "requiredWhenDefined", requiredWhenDefined);

const DetectionEditSchema = Yup.object().shape({
  name: Yup.string()
    .min(2, "Minimum 2 symbols")
    .max(50, "Maximum 50 symbols")
    .required("Name is required"),
  // description: Yup.string()
  //   .min(2, "Minimum 2 symbols")
  //   .max(500, "Maximum 500 symbols")
  //   .required("Detection is required"),
  image: Yup.mixed()
    .requiredWhenDefined()
    .test('required', "File is required", value => !(value && Object.keys(value).length === 0 && value.constructor === Object))
    .test('type', "Unsupported File Format", value => SUPPORTED_FORMATS.includes(value.type))
    .test('size', "File Size is too large", value => value.size >= FILE_SIZE)
});

const detectionTypes = ['Image', 'Video', 'Stream'];

export function NewDetectionPage() {

  const history = useHistory();

  const classes = useStyles();

  const btnRef = useRef();
  const ref = useRef(null);

  const [models, setModels] = React.useState([]);
  const [image, setImage] = React.useState();

  React.useEffect(() => {
    async function fetchData() {
      const result = await axios(`${BACKEND_URL}/models`);
      setModels(result.data);
    }
    fetchData();
  }, []);

  const initialValues = {
    "name": "",
    "detection_type": "Image",
    "model_id": 1,
    "description": ""
  }

  return (
    <div className={classes.root}>
      <Card>
        <CardHeader title="Create New Detection">
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
              setImage(null);
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
              detectionAPI.createDetection(values)
                .then(response => {
                  if (response.status >= 200 && response.status < 300) {
                    alert('New detection created successful.');
                    history.push('/detection');
                    history.go();
                  } else {
                    alert('Error status ' + String(response.status));
                    history.push('/detection');
                    history.go();
                  }
                });
            }}
          >
            {({ handleSubmit, setFieldValue, errors, resetForm }) => (
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
                      <Select name="detection_type" label="Detection Type">
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
                    />
                  </div>
                  <div className="form-group">
                    <label>Select File</label>
                    <br />
                    <input id="image" name="image" type="file" onChange={(event) => {
                      setFieldValue("image", event.currentTarget.files[0]);
                      setImage(event.currentTarget.files[0]);
                    }} />
                    <br />
                    {errors["image"] ?
                      <div className="text-danger">{errors["image"]}</div> :
                      ref.current && ref.current.values["image"] ?
                        <div className="text-success">{"File was chose correct"}</div> :
                        <>Please enter <b>{"Image"}</b></>
                    }
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
          <div className="text-center">
            {image && <img alt='selected' src={URL.createObjectURL(image)} className="img-thumbnail" />}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}