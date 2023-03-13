import _ from "lodash";
import { DataFrame } from "dataframe-js";
import fs from "fs";
import moment from "moment";

const mtsFormat = "x";
const dateFormat = "YYYY-MM-DD";
const datetimeFormat = `${dateFormat} HH:mm:ss`;

async function getDailyBalances(ccy, wallet) {
  const dataUrl = `./data/raw/${ccy}.json`;
  const data = JSON.parse(fs.readFileSync(dataUrl, "utf8"));

  const filteredData = _.filter(data, (row) => row.wallet === wallet);

  if (_.isEmpty(filteredData)) return;

  const dailyBalances = new DataFrame(
    _.map(filteredData, (row, index, array) => {
      const mts = moment(row.mts, mtsFormat);
      const amount = row.amount;
      const balance = row.balance;
      const date = mts.format(dateFormat);
      const datetime = mts.format(datetimeFormat);
      const prevBalance = _.get(array, [index - 1, "balance"], 0);
      const emptyFill = amount === 0 || prevBalance === 0 ? 1 : 0;
      return { date, datetime, amount, emptyFill, balance };
    })
  )
    .groupBy("date")
    .aggregate((group) => group.tail(1).select("balance").toArray());

  console.log(dailyBalances.head().show());

  return dailyBalances;
}

getDailyBalances("BTC", "exchange");
