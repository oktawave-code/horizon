package topics;

import play.data.validation.Constraints.Required;

public class Topic {

    @Required
    private String name;

    @Required
    private Integer partitionsNumber;

    public Topic() {}
    
    public Topic(String name, Integer partitionsNumber) {

        this.name = name;
        this.partitionsNumber = partitionsNumber;

    }

    public String getName() {
        return name;
    }

    public Integer getPartitionsNumber() { return partitionsNumber; }

}