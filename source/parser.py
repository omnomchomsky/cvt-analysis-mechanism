import xmltodict
import ast
import os
import logging
import argparse


class CoverityXMLParser:
    def __init__(self, path_to_cov_xml="index.xml", results_file="results.dat", log_file="py.log"):
        """
        :param path_to_cov_xml: Path to the index.xml generated by coverity
        :param results_file:  Optional path to existing results.dat.
        """
        with open(path_to_cov_xml) as fd:
            self.doc = xmltodict.parse(fd.read())
        self.results_file = results_file
        logging.basicConfig(filename=log_file, filemode="w", level=logging.INFO)

    def get_summary(self):
        """
        :return: Returns a dictionary of specific coverity options.
        """
        summary = {'_total': 0}
        for error in self.doc['coverity']['error']:
            summary['_total'] += 1
            key = "{}:{}".format(error['checker'], error['function'])
#            key = error['checker'] + ":" + error["function"] + ": "
            if key not in summary.keys():
                summary[key] = 1
            else:
                summary[key] += 1
#        for i in sorted(summary.keys()):
#            print i + ":" str(summary[i])
        return summary

    def old_results_exists(self):
        """
        :return: Returns true if a file with the name of the provided results_file name exists.
        """
        return os.path.isfile(self.results_file)

    def save_results(self,):
        with open(self.results_file, "w") as fd:
            fd.write(str(self.get_summary()))

    def get_old_results(self):
        """
        :return: Reads the data in the results_file and returns it as a dictionary
        """
        with open(self.results_file, "r") as fd:
            a = fd.read()
            return ast.literal_eval(a)

    @staticmethod
    def compare_keys(old, new):
        """
        :param old: Original results in dictionary form
        :param new:  New results in dictionary form
        :return: Pass/Fail boolean
        """
        set1 = set(old.keys())
        set2 = set(new.keys())
        if set2 - set1 != set([]):
            logging.info("Found new errors {}".format((set2 - set1)))
            return False
        return True

    @staticmethod
    def compare_values(old, new):
        """
        :param old: Original results in dictionary form
        :param new:  New results in dictionary form
        :return: Pass/Fail boolean
        """
        a = set(new.keys()) & set(old.keys())
        valid = True
        for i in a:
            if new[i] > old[i]:
                logging.info("There are more {} type errors than before".format(i))
                valid = False
        return valid

    def compare_results(self, old, new):
        """
        :param old: Original results in dictionary form
        :param new:  New results in dictionary form
        :return: Pass/Fail boolean
        """
        valid = True
        if not self.compare_keys(old, new):
            valid = False
        if not self.compare_values(old, new):
            valid = False
        return valid

    def generate_results(self):
        new_results = self.get_summary()
        if not self.old_results_exists():
            self.save_results()
        if self.compare_results(self.get_old_results(), new_results):
            self.save_results()


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-n', action='store', dest='input_index', default='index.xml',
                                 help='New input index.xml file created by cov-analysis')
    argument_parser.add_argument('-o', action='store', dest='data_file', default='results.dat',
                                 help='Data file for comparing the index against')
    argument_parser.add_argument('-l', action='store', dest='log_file', default='cvt_py_results.log',
                                 help="Log file where caught errors are stored")
    results = argument_parser.parse_args()
    a = CoverityXMLParser(path_to_cov_xml=results.input_index,
                          results_file=results.data_file,
                          log_file=results.log_file)
    a.generate_results()


if __name__ == "__main__":
    main()
