
import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { useHistory } from 'react-router-dom';
import { useParams } from "react-router-dom";

import { Card, CardHeader, CardHeaderToolbar, CardBody } from "../../../_metronic/_partials/controls";

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
    marginTop: theme.spacing(3),
  },
  paper: {
    width: '100%',
    marginBottom: theme.spacing(2),
  },
  table: {
    minWidth: 750,
    paddingRight: 15
  },
  tableWrapper: {
    overflowX: 'auto'
  },
}));

export function ViewDetectionPage() {
  const classes = useStyles();

  React.useEffect(() => {
    async function fetchData() {
      //   const result = await axios(`${BACKEND_URL}/detections`);
      //   setRows(result.data);
    }
    fetchData();
  }, []);

  const params = useParams();

  const history = useHistory();

  return (
    <div className={classes.root}>
      <Card>
        <CardHeader title={`Detection ID ${params.id}`}>
          <CardHeaderToolbar>
            <button
              type="button"
              className="btn btn-light"
              onClick={() => {
                history.push("/detection");
              }}
            >
              <i className="fa fa-arrow-left"></i>
              Back
            </button>
          </CardHeaderToolbar>
        </CardHeader>
        <CardBody>
          hello
        </CardBody>
      </Card>
    </div>
  );
}