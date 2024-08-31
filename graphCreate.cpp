#include <fstream>
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <memory>
#include <sstream>

class Node {
public:
    Node(float x_, float y_, float z_, int id_) 
        : x(x_), y(y_), z(z_), id(id_), g(999999999.0f), h(0), f(0), status(0), used(false), previous(nullptr) {}

    std::string name;
    int id;
    int status;
    float g;
    float h;
    float f;
    bool used;
    float x, y, z;

    Node* previous;
    std::vector<Node*> neighbors;
    std::vector<float> cost;
};

float distance(const Node* n, const Node* m) {
    return std::sqrt((n->x - m->x) * (n->x - m->x) + 
                     (n->y - m->y) * (n->y - m->y) + 
                     (n->z - m->z) * (n->z - m->z));
}

int main(int argc, char** argv) {
    if (argc != 9) {
        std::cerr << "Invalid arguments. Use --help for help.\n";
        return -1;
    }

    std::string fileName = argv[1];
    if (fileName == "--help" || fileName == "-h") {
        std::cout << "Usage: EXECUTABLE [output file name] [Max X] [Max Y] [Max Z] [Min X] [Min Y] [Min Z] [Resolution]\n";
        return 0;
    }

    float max_x = std::stof(argv[2]);
    float max_y = std::stof(argv[3]);
    float max_z = std::stof(argv[4]);
    float min_x = std::stof(argv[5]);
    float min_y = std::stof(argv[6]);
    float min_z = std::stof(argv[7]);
    float resolution = std::stof(argv[8]);

    int id_counter = 0;
    std::vector<std::shared_ptr<Node> > nodeList;

    for (float i = min_x; i <= max_x; i += resolution) {
        for (float j = min_y; j <= max_y; j += resolution) {
            for (float k = min_z; k <= max_z; k += resolution) {
                nodeList.push_back(std::make_shared<Node>(i, j, k, id_counter++));
            }
        }
    }

    std::cout << "Node count: " << nodeList.size() << std::endl;

    int n_counter = 0;
    int temp = 1;
    for (auto& n : nodeList) {
        n_counter++;
        if ((nodeList.size() / 100) * temp < n_counter) {
            std::cout << "%" << temp << std::endl;
            temp++;
        }

        for (auto& m : nodeList) {
            if (n->id != m->id &&
                std::abs(n->x - m->x) <= resolution &&
                std::abs(n->y - m->y) <= resolution &&
                std::abs(n->z - m->z) <= resolution) {

                n->neighbors.push_back(m.get());
                n->cost.push_back(distance(n.get(), m.get()));
            }
        }
    }

    std::ofstream file(fileName);
    std::ostringstream buffer;

    for (const auto& n : nodeList) {
        buffer << n->id << " " << std::fixed << std::setprecision(2) << n->x << " " << n->y << " " << n->z << "\n";
    }

    for (const auto& n : nodeList) {
        buffer << "NL " << n->id << " " << n->neighbors.size() << " ";
        for (size_t i = 0; i < n->neighbors.size(); i++) {
            buffer << n->neighbors[i]->id << " " << std::fixed << std::setprecision(2) << n->cost[i] << " ";
        }
        buffer << "\n";
    }

    file << buffer.str();
    file.close();

    return 0;
}
