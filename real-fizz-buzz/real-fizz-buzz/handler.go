package function

import (
	"fmt"
	consulStateStore "github.com/faasflow/faas-flow-consul-statestore"

	minioDataStore "github.com/faasflow/faas-flow-minio-datastore"
	faasflow "github.com/faasflow/lib/openfaas"

	"log"
	"os"
	"strconv"
	"time"
)

// Define provide definition of the workflow
func Define(flow *faasflow.Workflow, context *faasflow.Context) (err error) {
	dag := flow.Dag()
	dag.Node("start-node").Modify(func(data []byte) ([]byte, error) {
		if len(data) == 0 {
			data = []byte("0")
		}
		return data, nil
	})
	conditiondags := dag.ConditionalBranch("conditional-branch",
		[]string{"0", "1"},
		func(data []byte) []string {
			number, err := strconv.Atoi(string(data[:len(data)-1]))
			if err != nil {
				panic(err)
			}
			if number == 0 {
				log.Print("The number is divisible by 3")
				return []string{"fizz"}
			} else if number%5 == 0 {
				log.Print("The number is divisible by 5")
				return []string{"buzz"}
			} else {
				log.Print("The number is neither")
				return []string{"identity"}
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
		time.Sleep(3 * time.Second)
		return []byte(result), nil
	})

	conditiondags["buzz"].Node("node1").Modify(func(data []byte) ([]byte, error) {
		result := fmt.Sprintf("buzz-node1(%s)", string(data))
		time.Sleep(3 * time.Second)
		return []byte(result), nil
	})

	conditiondags["identity"].Node("node1").Modify(func(data []byte) ([]byte, error) {
		result := fmt.Sprintf("identity-node1(%s)", string(data))
		time.Sleep(3 * time.Second)
		return []byte(result), nil
	})
	// AddVertex with Aggregator

	dag.Node("end-node", faasflow.Aggregator(func(results map[string][]byte) ([]byte, error) {
		// results can be aggregated accross the branches
		result := ""
		for node, data := range results {
			result = result + " " + node + "=" + string(data)
		}
		return []byte(result), nil
	})).Modify(func(data []byte) ([]byte, error) {
		time.Sleep(3 * time.Second)
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
