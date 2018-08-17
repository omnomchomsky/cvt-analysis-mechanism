import xmltodict
import ast
import os
import logging


class CoverityXMLParser:
    def __init__(self, path_to_cov_xml="index.xml", results="results.dat"):
        with open(path_to_cov_xml) as fd:
            self.doc = xmltodict.parse(fd.read())
        self.results_file = results
        self.logger = logging.Logger("coverity_xml_parser_log", logging.INFO)

    def get_summary(self):
        summary = {'_total': 0}
        for error in self.doc['coverity']['error']:
            summary['_total'] += 1
            key = "{}:{}".format(error['checker'], error['function'])
            #key = error['checker'] + ":" + error["function"] + ": "
            if key not in summary.keys():
                summary[key] = 1
            else:
                summary[key] += 1
        #for i in sorted(summary.keys()):
        #    print i + ":" str(summary[i])
        return summary

    def old_results_exists(self):
        return os.path.isfile(self.results_file)

    def save_results(self,):
        with open(self.results_file, "w+") as fd:
            fd.write(str(self.get_summary()))

    def get_old_results(self):
        with open(self.results_file, "r") as fd:
            a = fd.read()
            return ast.literal_eval(a)

    def compare_keys(self,old,new):
        set1 = set(old.keys())
        set2 = set(new.keys())
        if set2 - set1 != set([]):
            self.logger.log(logging.INFO, "Found new errors {}".format((set2 - set1)))
            return False
        return True

    def compare_results(self, old, new):
        valid = self.compare_keys(old, new)
        return valid

    def generate_results(self):
        new_results = self.get_summary()
        if self.old_results_exists() or self.compare_keys(self.get_old_results(), new_results):
            self.save_results()
        return


def main():
    a = CoverityXMLParser()
    thing = a.get_summary()
    a.generate_results()
    #for i in sorted(thing.keys()):
    #    print "{} {}".format(i, thing[i])


if __name__ == "__main__":
    main()
