from mrjob.job import MRJob
from mrjob.step import MRStep
from datetime import datetime


class SearchDAU(MRJob):

    def mapper_get_users_by_date(self, _, line):
        userid, timestamp, action = map(int, line.split())
        date = datetime.fromtimestamp(timestamp).isoformat()[:10]
        yield ((date, userid), action)


    def reducer_group_users_by_date(self, key, value):
        if value == "search":
            yield (key[0], 1)

    def reducer_sum_unique_users(self, key, values):
        yield key, sum(values)

    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_users_by_date,
                   reducer=self.reducer_group_users_by_date),
            MRStep(reducer=self.reducer_sum_unique_users)
        ]


if __name__ == '__main__':
    SearchDAU.run()

s = SearchDAU(["user_activity_log.tsv"])
with s.make_runner() as runner:
    runner.run()
    output = s.parse_output(runner.cat_output())
    for line in sorted(output):
        print(*line, sep="\t")
