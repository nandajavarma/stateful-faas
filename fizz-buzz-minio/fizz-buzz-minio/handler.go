package function

import (
	"fmt"
	consulStateStore "github.com/faasflow/faas-flow-consul-statestore"

	minioDataStore "github.com/faasflow/faas-flow-minio-datastore"
	faasflow "github.com/faasflow/lib/openfaas"
	"log"
	"os"
	"strconv"
	// "time"
)

// Define provide definition of the workflow
func Define(flow *faasflow.Workflow, context *faasflow.Context) (err error) {
	dag := flow.Dag()
	dag.Node("start-node").Modify(func(data []byte) ([]byte, error) {
		if len(data) == 0 {
			data = []byte("aa-bb-cc")
		}
		return data, nil
	})
	conditiondags := dag.ConditionalBranch("conditional-branch",
		[]string{"fizz", "buzz"},
		func(data []byte) []string {
			number, err := strconv.Atoi(string(data[:len(data)-1]))
			if err != nil {
				panic(err)
			}
			if number%2 == 0 {
				log.Print("The number is even")
				return []string{"buzz"}
			} else {
				log.Print("The number is odd")
				return []string{"fizz"}
			}
		},
		faasflow.Aggregator(func(results map[string][]byte) ([]byte, error) {
			result := ""
			for condition, data := range results {
				result = result + "" + condition + "=" + string(data)
			}
			return []byte(result), nil
		}),
	)
	conditiondags["fizz"].Node("node1").Modify(func(data []byte) ([]byte, error) {
		result := fmt.Sprintf("fizz-node1(%s)", string(data))
		// time.Sleep(5 * time.Second)
		return []byte(result), nil
	})
	conditiondags["fizz"].Node("node2").Apply("func1").Modify(func(data []byte) ([]byte, error) {
		result := fmt.Sprintf("fizz-node2(%s)", string(data))
		// time.Sleep(5 * time.Second)
		return []byte(result), nil
	})
	conditiondags["fizz"].Edge("node1", "node2")

	conditiondags["buzz"].Node("node1").Modify(func(data []byte) ([]byte, error) {
		result := fmt.Sprintf("buzz-node1(%s)", string(data))
		// time.Sleep(5 * time.Second)
		return []byte(result), nil
	})
	conditiondags["buzz"].Node("node2").Apply("func2").Modify(func(data []byte) ([]byte, error) {
		result := fmt.Sprintf("buzz-node2(%s)", string(data))
		// time.Sleep(5 * time.Second)
		return []byte(result), nil
	})
	conditiondags["buzz"].Edge("node1", "node2")

	// AddVertex with Aggregator
	dag.Node("end-node", faasflow.Aggregator(func(results map[string][]byte) ([]byte, error) {
		// results can be aggregated accross the branches
		result := ""
		for node, data := range results {
			result = result + " " + node + "=" + string(data)
		}
		return []byte(result), nil
	})).Modify(func(data []byte) ([]byte, error) {
		// time.Sleep(5 * time.Second)
		log.Print("End data: ", string(data))
		return data, nil
	})

	dag.Edge("start-node", "conditional-branch")
	dag.Edge("conditional-branch", "end-node")

	return
}

// DefineStateStore provides the override of the default StateStore
func OverrideStateStore() (faasflow.StateStore, error) {
	consulss, err := consulStateStore.GetConsulStateStore(
		os.Getenv("consul_url"),
		os.Getenv("consul_dc"),
	)
	if err != nil {
		return nil, err
	}
	return consulss, nil
}

// ProvideDataStore provides the override of the default DataStore
func OverrideDataStore() (faasflow.DataStore, error) {
	miniods, err := minioDataStore.InitFromEnv()
	if err != nil {
		return nil, err
	}
	return miniods, nil
}
