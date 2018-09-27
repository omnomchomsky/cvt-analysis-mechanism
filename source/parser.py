import xmltodict
import ast
import os
import sys
import logging
import argparse


class CoverityXMLParser:
    def __init__(self, path_to_cov_xml="index.xml", results_file="results.dat", log_file="py.log", writable=False):
        """
        :param path_to_cov_xml: Path to the index.xml generated by coverity
        :param results_file:  Optional path to existing results.dat.
        """
        self.errors = list()
        self.writable = writable
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
        if self.writable:
            with open(self.results_file, "w") as fd:
                print("Updating Table")
                fd.write(str(self.get_summary()))

    def get_old_results(self):
        """
        :return: Reads the data in the results_file and returns it as a dictionary
        """
        with open(self.results_file, "r") as fd:
            a = fd.read()
            return ast.literal_eval(a)

    def compare_keys(self, old, new):
        """
        :param self
        :param old: Original results in dictionary form
        :param new:  New results in dictionary form
        :return: Pass/Fail boolean
        """
        set1 = set(old.keys())
        set2 = set(new.keys())
        diff_set = set2 - set1
        if diff_set != set([]):
            error_message = "Found new errors {}".format(list(diff_set))
            logging.info(error_message)
            self.errors = self.errors + list(diff_set)
            return False
        return True

    def compare_values(self, old, new):
        """
        :param self
        :param old: Original results in dictionary form
        :param new:  New results in dictionary form
        :return: Pass/Fail boolean
        """
        a = set(new.keys()) & set(old.keys())
        valid = True
        for i in a:
            if new[i] > old[i]:
                if i != "_total":
                    error_string = "There are more {} type errors than before".format(i)
                    logging.info(error_string)
                    self.errors.append(error_string)
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
            print "Generating new data table"
            self.save_results()
        elif self.compare_results(self.get_old_results(), new_results):
            print "No new errors."
            self.save_results()
        else:
            print self.errors
            sys.exit("Found {} static analysis error(s)".format(len(self.errors)))


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-n', action='store', dest='input_index', default='index.xml',
                                 help='New input index.xml file created by cov-analysis')
    argument_parser.add_argument('-o', action='store', dest='data_file', default='results.dat',
                                 help='Data file for comparing the index against')
    argument_parser.add_argument('-l', action='store', dest='log_file', default='cvt_py_results.log',
                                 help="Log file where caught errors are stored")
    argument_parser.add_argument('-w', action='store_true', dest='writable')
    results = argument_parser.parse_args()
    a = CoverityXMLParser(path_to_cov_xml=results.input_index,
                          results_file=results.data_file,
                          log_file=results.log_file,
                          writable=results.writable)
    a.generate_results()


if __name__ == "__main__":
    main()
