import React, { useRef } from 'react';
import { Formik, Form, Field } from "formik";
import { Image, Row, Col } from "react-bootstrap";
import * as Yup from "yup";
import { useHistory } from 'react-router-dom';
import { Input, Select } from "../../../_metronic/_partials/controls";
import 'chart.js';
import ReactHlsPlayer from "react-hls-player";
import ReactPlayer from 'react-player';

import axios from 'axios';
import { BACKEND_URL } from '../../../config';

import {
  Card, CardHeader, CardBody
} from "../../../_metronic/_partials/controls";

import detectionAPI from '../../utils/DetectionAPI';

const DetectionEditSchema = Yup.object().shape({
  Url: Yup.string()
    .min(2, "Minimum 2 symbols")
    .required("Stream URL is required"),
  // Images: Yup.mixed()
  //   .test('len', "Please select Face Images", values => values && values.length > 0)
  //   .test('type', "Unsupported File Format", values => {
  //     let flag = true;
  //     if (!values) return true;
  //     values.forEach(value => {
  //       if (!SUPPORTED_IMAGE_FORMATS.includes(value.type)) flag = false;
  //     });
  //     return flag;
  //   })
});

const SUPPORTED_IMAGE_FORMATS = [
  "image/jpg",
  "image/jpeg",
  "image/gif",
  "image/png"
];
const SUPPORTED_VIDEO_FORMATS = [
  "video/mp4"
]

export function DashboardPage() {

  const [images, setImages] = React.useState();
  const [url, setUrl] = React.useState("");
  const [isSubmited, setIsSubmited] = React.useState(false);
  const [imageUrls, setImageUrls] = React.useState();
  const [imageUrl, setImageUrl] = React.useState();

  const btnRef = useRef();
  const ref = useRef(null);

  const getData = async () => {
    try {
      // const result = await axios(`${BACKEND_URL}/faces/image`);
      // console.log(result)
      setImageUrl("http://115.78.96.177/api/v1//faces/rimage/" + String(new Date().valueOf()));

    } catch (err) {
      console.error(err.message);
    }
  };

  React.useEffect(() => {
    // getData()
    const interval = setInterval(() => {
      getData()
    }, 500)
    return () => clearInterval(interval)
  }, []);

  const initialValues = {
    Url: "",
    images: []
  }

  return (
    <div>
      <Card>
        <CardHeader title={`Face Recognition`} />
        <CardBody>
          <Formik
            innerRef={ref}
            enableReinitialize={true}
            initialValues={initialValues}
            validationSchema={DetectionEditSchema}
            onSubmit={(values) => {
              // console.log(values.Url);
              // console.log(images);

              setUrl(values.Url);
              detectionAPI.createFacereg(values.Url, images)
                .then(response => {
                  if (response.status >= 200 && response.status < 300) {
                    
                    alert('New detection created successful.');
                    setIsSubmited(true);
                    // history.push(`/detection/${response.data.id}`);
                    // history.go();
                  } else {
                    alert('Error status ' + String(response.status));
                    // history.push('/detection/');
                    // history.go();
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
                        name="Url"
                        component={Input}
                        placeholder="Stream URL"
                        label="Stream Url"
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Select Face Images</label>
                    <Row >
                      {imageUrls && imageUrls.map(url =>
                        <Col xs={4} md={3}>
                          <Image src={url} alt={url} thumbnail key={url} />
                        </Col>
                      )}
                    </Row>
                    <input id="images" name="images" type="file" multiple onChange={(event) => {
                      setFieldValue("images", event.currentTarget.files);
                      setImages(event.currentTarget.files);
                      setImageUrls(Array.from(event.currentTarget.files).map(f => URL.createObjectURL(f)));
                    }} />
                    <br />
                    {errors["images"] ?
                      <div className="text-danger">{errors["image"]}</div> :
                      ref.current && ref.current.values["images"] && ref.current.values["images"].length > 0 ?
                        <div className="text-success">{"Face images are chose"}</div> :
                        <>Please select <b>{"Face Images"}</b></>
                    }
                  </div>
                  <button className="btn btn-primary"f
                    type="submit"
                    // ref={btnRef}
                    // style={{ display: "none" }}
                    onSubmit={() => handleSubmit()}
                  >Submit</button>
                </Form>
                <br />
                {isSubmited && <div>
                  <label>Result</label>
                  <div className="d-flex flex-row">
                    <ReactPlayer
                      url={url}
                      playing
                      muted
                      width="48%"
                      height="auto"
                    />
                    <Image
                      // src={url}
                      src={imageUrl}
                      width="48%"
                      height="auto"
                      style={{ marginLeft: 30 }}
                    />
                  </div>
                </div>}
              </>
            )}
          </Formik>
        </CardBody>
      </Card>
    </div>
  );
}