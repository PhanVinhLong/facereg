import React from "react";
import { LayoutSplashScreen } from "../../../../_metronic/layout";
import authAPI from "../../../utils/AuthAPI";
import { createBrowserHistory } from 'history';


function Logout() {

  const history = createBrowserHistory();

  React.useEffect(() => {
    authAPI.logout()
      .then(() => {
        history.push('/auth/login');
        history.go();
      });
  });

  return (
    <LayoutSplashScreen />
  )
}

export default Logout;
