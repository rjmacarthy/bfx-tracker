import _ from "lodash";
import moment from "moment";
import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const mtsFormat = "x";
const dateFormat = "YYYY-MM-DD";
const datetimeFormat = `${dateFormat} HH:mm:ss`;
const METHOD = "getLedgers";
const URL = "https://report.bitfinex.com/api/json-rpc";
const LIMIT = 1000;
const DATE_FROM = moment("2013-01-01", dateFormat).valueOf();
const DATE_TO = moment().valueOf();
const AUTH_TOKEN = process.env.BFX_AUTH_TOKEN;
const DEFAULT_HEADERS = {
  "bfx-nonce": moment().valueOf(),
  "Content-Type": "application/json",
};

const getPayload = (ccy) => ({
  auth: {
    authToken: AUTH_TOKEN,
  },
  method: METHOD,
  params: {
    start: DATE_FROM,
    end: DATE_TO,
    limit: LIMIT,
    symbol: [ccy],
  },
});

const fetchLedgers = async (ccy) => {
  const payload = getPayload(ccy);
  const headers = {
    ...DEFAULT_HEADERS,
  };
  const { data } = await axios.post(URL, payload, { headers });
  return _.get(data, "result.res", []);
};

async function getDailyBalances(ccy, wallet) {
  const data = await fetchLedgers(ccy);

  if (_.isEmpty(data)) return;

  return _.map(
    _.groupBy(
      _.map(
        _.filter(data, (row) => row.wallet === wallet),
        (row, index, array) => {
          const mts = moment(row.mts, mtsFormat);
          const amount = row.amount;
          const balance = row.balance;
          const date = mts.format(dateFormat);
          const datetime = mts.format(datetimeFormat);
          const prevBalance = _.get(array, [index - 1, "balance"], 0);
          const emptyFill = amount === 0 || prevBalance === 0 ? 1 : 0;
          return { date, datetime, amount, emptyFill, balance };
        }
      ),
      "date"
    ),
    (rows, date) => ({
      date,
      balance: _.get(_.last(rows), "balance", 0),
    })
  );
}

getDailyBalances("BTC", "exchange");
getDailyBalances("ETH", "exchange");
