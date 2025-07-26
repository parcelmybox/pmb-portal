import {LOCATION_NAMES} from "../constants";


const SHIPPING = {
    name: "Shipping",
    description: "Shipping description"
};

const BUYING = {
    name: "Buying",
    description: "Buying description"
};


export const SERVICES = {
    [LOCATION_NAMES.BANGALORE]: [SHIPPING, BUYING],
    [LOCATION_NAMES.CHENNAI]: [SHIPPING],
}