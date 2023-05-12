function call(sender, data) {
    if (sender.loading()) {
        return {
            done: function () {
            }, always: function () {
            }, fail: function () {
            }
        }
    }
    sender.loading(true);
    return $.ajax({
        url: ".",
        method: "POST",
        headers: {'X-CSRFToken': $("#celery").data("token")},
        data: JSON.stringify(data),
        dataType: "json"
    })
        .always(function () {
            sender.loading(false);
        })
}

function Info(opts) {
    var self = this;
    self.raw = opts;
    self.task = opts.parent;
    self.id = ko.observable(opts.id)
    self.args = ko.observable(opts.args)
    self.kwargs = ko.observable(JSON.stringify(opts.kwargs))
}

function Extra(opts) {
    var self = this;
    self.raw = opts;
    var entries = [];
    Object.keys(opts).forEach(function (k) {
        entries.push([k, opts[k]])
    })
    self.entries = ko.observableArray(entries);
}

function Func(opts) {
    var self = this;
    self.raw = opts;
    self.name = ko.observable(opts.data);
    self.doc = ko.observable();
    self.signature = ko.observable();
    self.loading = ko.observable(false);
    self.worker = opts.parent;
    self.inspect = function () {
        return call(self, {
            "op": "func",
            "name": self.name()
        })
            .done(function (response) {
                console.log(response)
                ko.mapping.fromJS(response, {}, self);
                self.worker.selectedFunc(self);
                self.worker.display("func_details");
            })
    }
}

function Task(opts) {
    var self = this;
    self.raw = opts;
    self.time_start = ko.observable();
    self.info = ko.observable();
    self.args = ko.observable();
    self.kwargs = ko.observable();
    self.extra = ko.observable();
    self.loading = ko.observable(false);
    self.worker = opts.parent;
    ko.mapping.fromJS(opts.data, mapping, self);

    self.start = ko.computed(function () {
        if (self.time_start()) {
            return new Date(self.time_start() * 1000);
        }
    });
    self.inspect = function () {
        return call(self, {
            "op": "task",
            "id": self.id()
        })
            .done(function (response) {
                self.extra(response.extra);
                self.kwargs(JSON.stringify(response.info.kwargs));
                self.worker.selectedTask(self);
                self.worker.display("task_details");
            })
    };
}

var mapping = {
    workers: {
        create: function (options) {
            return new Worker(options);
        }
    },
    active: {
        create: function (options) {
            return new Task(options);
        }
    },
    registered: {
        create: function (options) {
            return new Func(options);
        }
    },
    info: {
        create: function (options) {
            return new Info(options);
        }
    },
    extra: {
        create: function (options) {
            return new Extra(options);
        }
    },
}

function Worker(opts) {
    var self = this;
    self.raw = opts;
    self.parent = opts.parent;
    self.name = ko.observable();
    self.selectedFunc = ko.observable();
    self.selectedTask = ko.observable();
    self.tab = ko.observable(1);
    self.display = ko.observable('summary');
    self.tab.subscribe(function () {
        self.display("summary");
    });
    self.active = ko.observableArray([]);
    self.reserved = ko.observableArray([]);
    self.registered = ko.observableArray([]);
    self.scheduled = ko.observableArray([]);
    ko.mapping.fromJS(opts.data, mapping, self);
    ko.mapping.fromJS(opts.data.stats, {}, self);
    self.loading = ko.observable(false);
    self.inspect = function () {
        self.parent.loading(true);
        return call(self, {
            "op": "worker",
            "name": self.name()
        }).done(function (response) {
            ko.mapping.fromJS(response, mapping, self);
            self.tab(1);
        }).always(function () {
            self.parent.loading(false);
        })
    }
}

function CeleryModel() {
    var self = this;
    self.workers = ko.observableArray([]);
    self.tab = ko.observable(1);
    self.message = ko.observable();
    self.fetched = ko.observable(false);
    self.loading = ko.observable(false);
    self.interval = ko.observable(0);
    self.display = ko.observable("summary");
    self.intervals = ko.observableArray([0, 1, 10, 30, 60]);
    self.interval.subscribe(function (value) {
        if (value > 0) {
            setTimeout(self.refresh, value * 1000);
        }
    });
    self.refresh = function () {
        var requests = [];
        self.loading(true);
        $.each(self.workers(), function (idx, worker) {
            requests.push(worker.inspect());
        });
        $.when.apply(null, requests).then(function () {
            self.loading(false);
            if (self.interval() > 0) {
                setTimeout(self.refresh, self.interval() * 1000);
            }
        });
    };
    self.terminate = function () {
        call(self, {"op": "terminate_all"})
            .done(function (response) {
                self.stats().done(function () {
                    $.each(self.workers(), function (i, e) {
                        e.inspect();
                    })
                });
            })
    }
    self.testTask = function () {
        self.message("Invoking....");
        call(self, {"op": "test"})
            .done(function (response) {
                self.message("Test task invoked");
                self.stats().done(function () {
                    $.each(self.workers(), function (i, e) {
                        e.inspect();
                    })
                });
            })
    }
    self.purge = function () {
        call(self, {"op": "purge"})
            .done(function (response) {
                self.stats().done(function () {
                    $.each(self.workers(), function (i, e) {
                        e.inspect();
                    })
                });
            })
    }
    self.stats = function () {
        return call(self, {"op": "stats"})
            .done(function (response) {
                var ret = [];
                $.each(response.stats, function (k, v) {
                    v.name = k;
                    ret.push(v);
                });
                ko.mapping.fromJS({"workers": ret,}, mapping, self);
                self.fetched(true);
            })
    }
}