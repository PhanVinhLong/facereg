/* eslint-disable no-script-url,jsx-a11y/anchor-is-valid */
import React from "react";

export function HeaderMenu({ layoutProps }) {

    return <div
        id="kt_header_menu"
        className={`header-menu header-menu-mobile ${layoutProps.ktMenuClasses}`}
        {...layoutProps.headerMenuAttributes}
    >
        {/*begin::Header Nav*/}
        
        {/*end::Header Nav*/}
    </div>;
}
